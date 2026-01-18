"""
vCard/VCF Field Parser.

This module provides functions to parse individual fields from vCard (VCF) files.
It supports vCard versions 2.1, 3.0, and 4.0, handling various field types
including addresses, names, emails, multimedia tags, and more.

vCard format uses semicolons (;) as field separators and colons (:) as
key-value separators. Some fields may span multiple lines.
"""
import typing

from . import vcard_multimedia_helper

# vCard format separators
TAG_FIELD_SEPARATOR = ";"  # Separates field components
KEY_VALUE_SEPARATOR = ":"  # Separates key from value
TYPE_ASSIGNMENT_OR_LABEL_SEPARATOR = "="  # Used in TYPE=value constructs

# Simple keys that don't require special parsing - just key:value pairs
# Examples: ANNIVERSARY:19901021, FN:Dr. John Doe, GENDER:F
SIMPLE_KEYS = [
    "AGENT", "ANNIVERSARY", "BDAY", "CALADRURI", "CALURI", "CLASS", "FBURL",
    "FN", "GENDER", "KIND", "LANG", "MAILER", "NICKNAME", "NOTE", "PRODID",
    "PROFILE", "REV", "ROLE", "SORT-STRING", "SOURCE", "TITLE", "TZ", "URL",
    "VERSION", "XML"
]


def parse_simple_tag(file_line: str) -> str:
    """
    Parse a simple vCard tag (key:value format).
    
    Handles cases where the value contains colons (e.g., URLs).
    Splits on the first colon and joins everything after it.
    
    Args:
        file_line: vCard line in format "KEY:value" or "KEY:value:with:colons"
        
    Returns:
        The value portion (everything after the first colon)
        
    Example:
        >>> parse_simple_tag("FN:John Doe")
        'John Doe'
        >>> parse_simple_tag("URL:http://example.com/path")
        'http://example.com/path'
    """
    # Split on colon and join everything after the first one
    # This handles URLs and other values with multiple colons
    return "".join(file_line.split(KEY_VALUE_SEPARATOR)[1:])


def parse_address_tag(address_line: str) -> dict:
    """
    Parse an ADR (address) tag from a vCard.
    
    Address format: ADR;TYPE=HOME:;;123 Main St;City;State;12345;USA
    Some fields may be empty.
    
    Args:
        address_line: vCard address line
        
    Returns:
        Dictionary with address type as key and address string as value
        Example: {"HOME": "123 Main St City State 12345 USA"}
    """
    addr_line_split = address_line.split(TAG_FIELD_SEPARATOR)

    # Extract address components by iterating backwards until we hit the colon
    address_components_reverse = []
    for elem in addr_line_split[::-1]:
        if KEY_VALUE_SEPARATOR in elem:
            break
        address_components_reverse.append(elem)

    # Reverse to get correct order and join
    address = " ".join(address_components_reverse[::-1])

    # Extract address type (HOME, WORK, etc.)
    address_type = ""
    if len(addr_line_split) > 1:
        if addr_line_split[1].startswith("TYPE"):
            # Format: TYPE=HOME
            address_type = (
                addr_line_split[1]
                .split(TYPE_ASSIGNMENT_OR_LABEL_SEPARATOR)[1]
                .split(KEY_VALUE_SEPARATOR)[0]
            )
        else:
            # Format: HOME (without TYPE= prefix)
            address_type = addr_line_split[1]

    return {address_type: address.strip()}


def parse_categories_tag(category_line: str) -> tuple:
    """
    Parse a CATEGORIES tag from a vCard.
    
    Categories are comma-separated and returned sorted alphabetically.
    
    Args:
        category_line: vCard categories line (e.g., "CATEGORIES:swimmer,biker")
        
    Returns:
        Sorted tuple of category strings
        
    Example:
        >>> parse_categories_tag("CATEGORIES:swimmer,biker")
        ('biker', 'swimmer')
    """
    # Extract value and split by comma, then sort
    value = "".join(category_line.split(KEY_VALUE_SEPARATOR)[1:])
    return tuple(sorted(value.split(",")))


def parse_clientpidmap_tag(clientpidmap_line: str) -> dict:
    """
    Parse a CLIENTPIDMAP tag from a vCard.
    
    Format: CLIENTPIDMAP;urn:value
    
    Args:
        clientpidmap_line: vCard CLIENTPIDMAP line
        
    Returns:
        Dictionary mapping PID source identifier to URN
    """
    clientpidmap_split = clientpidmap_line.split(TAG_FIELD_SEPARATOR)
    urn = clientpidmap_split[1]
    pid_source_identifier = clientpidmap_split[0].split(KEY_VALUE_SEPARATOR)[1]
    return {pid_source_identifier: urn}


def parse_email_tag(email_line: str) -> dict:
    """
    Parse an EMAIL tag from a vCard.
    
    Format: EMAIL;TYPE=INTERNET:email@example.com
    
    Args:
        email_line: vCard email line
        
    Returns:
        Dictionary with email type as key and email address as value
    """
    return helper_match_generic_label_and_types(email_line)


def parse_geo_tag(geo_line: str) -> dict:
    """
    Parse a GEO (geographic coordinates) tag from a vCard.
    
    Supports vCard 2.1/3.0 format: GEO:lat;lon
    and vCard 4.0 format: GEO;TYPE=work:geo:lat,lon
    
    Args:
        geo_line: vCard GEO line
        
    Returns:
        Dictionary with "latitude" and "longitude" keys
    """
    geo_line_split = geo_line.split(KEY_VALUE_SEPARATOR)
    lat, lon = "", ""

    if len(geo_line_split) == 2:
        # vCard 2.1 or 3.0 format: GEO:lat;lon
        lat, lon = geo_line_split[1].split(TAG_FIELD_SEPARATOR)
    elif len(geo_line_split) == 3:
        # vCard 4.0 format: GEO;TYPE=work:geo:lat,lon
        lat, lon = geo_line_split[2].split(",")

    return {"latitude": lat, "longitude": lon}


def parse_instant_messenger_handle_tag(impp_line: str) -> dict:
    """
    Parse an IMPP (instant messaging) tag from a vCard.
    
    Format: IMPP;TYPE=xmpp:handle@example.com
    
    Args:
        impp_line: vCard IMPP line
        
    Returns:
        Dictionary with "type" and "handle" keys
    """
    _, impp_type, impp_handle = impp_line.split(KEY_VALUE_SEPARATOR)
    return {"type": impp_type, "handle": impp_handle}


def parse_mailing_label_tag(label_line: str) -> dict:
    """
    Parse a LABEL tag from a vCard.
    
    Format: LABEL;TYPE=HOME:123 Main St...
    
    Args:
        label_line: vCard LABEL line
        
    Returns:
        Dictionary with label type as key and label text as value
    """
    return helper_match_generic_label_and_types(label_line)


def parse_member_tag(member_line: str) -> dict:
    """
    Parse a MEMBER tag from a vCard.
    
    Format: MEMBER;VALUE=uri:urn:uuid:...
    
    Args:
        member_line: vCard MEMBER line
        
    Returns:
        Dictionary mapping member ID type to member ID value
    """
    member_line_split = member_line.split(KEY_VALUE_SEPARATOR)
    _, member_id_type = member_line_split[0], member_line_split[1]
    member_id_value = KEY_VALUE_SEPARATOR.join(member_line_split[2:])
    return {member_id_type: member_id_value}


def parse_name_tag(name_line: str) -> dict:
    """
    Parse an N (name) tag from a vCard.
    
    Format: N:Doe;John;F;; (family;given;additional;prefix;suffix)
    
    Args:
        name_line: vCard N line
        
    Returns:
        Dictionary with name components:
        - family_name
        - given_name
        - additional_middle_names
        - honorific_prefixes
        - honorific_suffixes
    """
    name_line_split = name_line.split(TAG_FIELD_SEPARATOR)
    subname_key_types = [
        "family_name",
        "given_name",
        "additional_middle_names",
        "honorific_prefixes",
        "honorific_suffixes"
    ]
    return helper_match_subkey_types_and_values(subname_key_types, name_line_split)


def return_name_tag_formatted(name_tag_field: dict) -> str:
    """
    Format a name tag dictionary into a single string.
    
    Concatenates all name components in order.
    
    Args:
        name_tag_field: Dictionary with name components (from parse_name_tag)
        
    Returns:
        Concatenated name string
        
    Example:
        >>> return_name_tag_formatted({
        ...     'family_name': 'Kennedy',
        ...     'given_name': 'John',
        ...     'additional_middle_names': 'F'
        ... })
        'KennedyJohnF'
    """
    name = ""
    for name_label in name_tag_field:
        name += name_tag_field[name_label]
    return name


def parse_organization_tag(organization_line: str) -> typing.Union[str, dict]:
    """
    Parse an ORG (organization) tag from a vCard.
    
    Can be simple (single value) or have subfields.
    
    Args:
        organization_line: vCard ORG line
        
    Returns:
        String for simple format, or dictionary with subfields:
        - organization_name
        - collective_organization_name
        - organizational_unit_name
        
    Reference:
        https://www.itu.int/ITU-T/formal-language/itu-t/x/x520/2012/SelectedAttributeTypes.html
    """
    organization_line_split = organization_line.split(TAG_FIELD_SEPARATOR)

    if len(organization_line_split) == 1:
        # Simple format: ORG:Acme Corp
        return organization_line.split(KEY_VALUE_SEPARATOR)[1]
    else:
        # Complex format with subfields
        sub_org_key_types = [
            "organization_name",
            "collective_organization_name",
            "organizational_unit_name"
        ]
        return helper_match_subkey_types_and_values(
            sub_org_key_types, organization_line_split
        )


def parse_related_tag(related_line: str) -> dict:
    """
    Parse a RELATED tag from a vCard.
    
    Format: RELATED;TYPE=contact:urn:uuid:...
    
    Args:
        related_line: vCard RELATED line
        
    Returns:
        Dictionary with relation type as key and relation value
    """
    return helper_match_generic_label_and_types(related_line)


def parse_telephone_tag(telephone_textline: str) -> dict:
    """
    Parse a TEL (telephone) tag from a vCard.
    
    Format: TEL;TYPE=CELL:+1234567890
    
    Args:
        telephone_textline: vCard TEL line
        
    Returns:
        Dictionary with phone type as key and phone number as value
    """
    return helper_match_generic_label_and_types(telephone_textline)


def parse_uuid_tag(uuid_textline: str) -> dict:
    """
    Parse a UID tag from a vCard.
    
    Format: UID:urn:uuid:...
    
    Args:
        uuid_textline: vCard UID line
        
    Returns:
        Dictionary with UID type as key and UID data as value
    """
    uid_line_split = uuid_textline.split(KEY_VALUE_SEPARATOR)
    uid_type = uid_line_split[1]
    uid_data = KEY_VALUE_SEPARATOR.join(uid_line_split[2:])
    return {uid_type: uid_data}


def parse_multimedia_tag(multimedia_tag_line: str) -> dict:
    """
    Parse a multimedia tag (PHOTO, SOUND, LOGO, KEY) from a vCard.
    
    Multimedia tags can appear in 6 different formats:
    
    1. <TAG-NAME>;<TAG-TYPE>:<TAG-DATA-URL>
    2. <TAG-NAME>;<TAG-TYPE>;ENCODING=BASE64:[base64-data]
    2a. <TAG-NAME>;ENCODING=BASE64;<TAG-TYPE>:[base64-data] (non-standard)
    3. <TAG-NAME>;TYPE=<TAG-TYPE>:<TAG-DATA-URL>
    4. <TAG-NAME>;TYPE=<TAG-TYPE>;ENCODING=b:[base64-data]
    5. <TAG-NAME>;MEDIATYPE=<TAG-MIME-TYPE>:<TAG-DATA-URL>
    6. <TAG-NAME>:data:<TAG-MIME-TYPE>;base64,[base64-data]
    
    Note: Case 2a isn't documented in the vCard spec but is used in practice.
    
    Args:
        multimedia_tag_line: vCard multimedia line (tag name prefix removed)
        
    Returns:
        Dictionary with keys:
        - tag_type: Media type (e.g., "jpeg")
        - tag_data: Base64-encoded data (if present)
        - tag_url: URL to media (if present)
        - tag_mime_type: MIME type (if present)
        
    Raises:
        Exception: If the multimedia tag format cannot be parsed
    """
    multimedia_tag_line_split = multimedia_tag_line.split(TAG_FIELD_SEPARATOR)
    tag_type, tag_data, tag_url, tag_mime_type = "", "", "", ""

    if len(multimedia_tag_line_split) == 3:
        # Case 2, 2a, or 4
        if TYPE_ASSIGNMENT_OR_LABEL_SEPARATOR in multimedia_tag_line_split[1]:
            if multimedia_tag_line_split[1] == "ENCODING=BASE64":
                # Case 2a: ENCODING=BASE64 comes before TYPE
                tag_type, tag_data = multimedia_tag_line_split[2].split(
                    KEY_VALUE_SEPARATOR
                )
            else:
                # Case 4: TYPE=<type>;ENCODING=b
                tag_type = (
                    multimedia_tag_line_split[1]
                    .split(TYPE_ASSIGNMENT_OR_LABEL_SEPARATOR)[1]
                )
                tag_data = (
                    multimedia_tag_line_split[2]
                    .split(KEY_VALUE_SEPARATOR)[1]
                )
        else:
            # Case 2: TYPE;ENCODING=BASE64
            tag_type = (
                multimedia_tag_line_split[2]
                .split(KEY_VALUE_SEPARATOR)[0]
            )
            tag_data = (
                multimedia_tag_line_split[-1]
                .split(KEY_VALUE_SEPARATOR)[1]
            )

    elif len(multimedia_tag_line_split) == 2:
        # Case 1, 3, 5, or 6
        if multimedia_tag_line_split[1].startswith("TYPE"):
            # Case 3: TYPE=<type>:url
            multimedia_type_decl_split = multimedia_tag_line_split[1].split(
                KEY_VALUE_SEPARATOR
            )
            tag_type = (
                multimedia_type_decl_split[0]
                .split(TYPE_ASSIGNMENT_OR_LABEL_SEPARATOR)[1]
            )
            tag_url = multimedia_type_decl_split[1]

        elif multimedia_tag_line_split[1].startswith("MEDIATYPE"):
            # Case 5: MEDIATYPE=<mime>:url
            multimedia_mediatype_decl_split = multimedia_tag_line_split[1].split(
                KEY_VALUE_SEPARATOR
            )
            tag_mime_type = (
                multimedia_mediatype_decl_split[0]
                .split(TYPE_ASSIGNMENT_OR_LABEL_SEPARATOR)[1]
            )
            tag_url = multimedia_mediatype_decl_split[1]

        elif multimedia_tag_line_split[1].startswith("base64"):
            # Case 6: data:mime;base64,data
            tag_mime_type = (
                multimedia_tag_line_split[0]
                .split(KEY_VALUE_SEPARATOR)[-1]
            )
            tag_data = multimedia_tag_line_split[1].split(",")[1]

        else:
            # Case 1: TYPE:url
            tag_type_and_url_split = multimedia_tag_line_split[1].split(
                KEY_VALUE_SEPARATOR
            )
            tag_type = tag_type_and_url_split[0]
            tag_url = ":".join(tag_type_and_url_split[1:])

    else:
        raise ValueError(
            f"Can't parse multimedia tag: '{multimedia_tag_line}'"
        )
    
    return helper_match_subkey_types_and_values(
        vcard_multimedia_helper.get_multimedia_tag_list(),
        [tag_type, tag_data, tag_url, tag_mime_type],
        contains_tag_name=False
    )


# Helper functions

def helper_match_subkey_types_and_values(
    subkey_names: typing.List[str],
    values: typing.List[str],
    contains_tag_name: bool = True
) -> dict:
    """
    Match subkey names with their corresponding values into a dictionary.
    
    Given lists of labels and values, creates a dictionary mapping labels
    to values, filtering out empty values.
    
    Args:
        subkey_names: List of field names (e.g., ["family_name", "given_name"])
        values: List of corresponding values
        contains_tag_name: If True, assumes first value contains tag name
                          and extracts the actual value after the colon
                          
    Returns:
        Dictionary mapping non-empty subkeys to their values
        
    Raises:
        ValueError: If the number of subkeys doesn't match the number of values
    """
    if contains_tag_name:
        # Strip the actual tag name from the first value
        values[0] = values[0].split(KEY_VALUE_SEPARATOR)[1]

    if len(subkey_names) != len(values):
        raise ValueError(
            f"Contents of line don't match specifications! "
            f"Only {len(values)} subfields found, but {len(subkey_names)} are required"
        )
    
    # Create pairs of (name, value) for non-empty values
    label_and_data_pairs = tuple(
        (name, value) for name, value in zip(subkey_names, values) if value
    )

    # Build result dictionary
    result_dict = {}
    for name, value in label_and_data_pairs:
        result_dict[name] = value

    return result_dict


def helper_match_generic_label_and_types(text_line: str) -> dict:
    """
    Parse a generic vCard line with TYPE parameter.
    
    Handles lines of the form: <KEY>;TYPE=<KEY_TYPE>:<KEY_DATA>
    or <KEY>;<KEY_TYPE>:<KEY_DATA>
    
    Args:
        text_line: vCard line to parse
        
    Returns:
        Dictionary with type as key and data as value
        Example: {"INTERNET": "email@example.com"}
    """
    text_line_split = text_line.split(KEY_VALUE_SEPARATOR)
    data = KEY_VALUE_SEPARATOR.join(text_line_split[1:])

    # Extract type from either TYPE=value or just value format
    data_type = ""
    if TYPE_ASSIGNMENT_OR_LABEL_SEPARATOR in text_line_split[0]:
        # Format: TYPE=value
        data_type = text_line_split[0].split("=")[1]
    else:
        # Format: value (without TYPE=)
        data_type = text_line_split[0].split(TAG_FIELD_SEPARATOR)[1]

    return {data_type: data}
