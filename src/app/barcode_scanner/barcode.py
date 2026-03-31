#!/usr/bin/env python3
"""
GS1 Barcode Class Decoder
------------------------
A Python module that decodes GS1 barcodes and creates a class with attributes
for each value in the barcode.

Usage:
    from gs1_decoder import Barcode

    # Create a barcode object
    b = Barcode("01095011010209171719050810AB-123")

    # Access attributes directly
    print(b.gtin)          # "09501101020"
    print(b.batch_lot)     # "AB-123"
    print(b.use_by)        # "2019-05-08"

    # Get all values as a dictionary
    print(b.as_dict())

    # Get all values as JSON
    print(b.as_json())
"""

import json
from typing import Dict, Optional, Any


class Barcode:
    """
    A class representing a decoded GS1 barcode.
    Attributes are dynamically created based on the Application Identifiers found.
    """

    # GS1 Application Identifiers (AI) with their lengths and attribute mappings
    # Format: AI: (name, total_length, is_fixed_length, attribute_name)
    AI_DEFINITIONS = {
        "00": ("SSCC", 18, True, "sscc"),
        "01": ("GTIN", 14, True, "gtin"),
        "02": ("CONTENT GTIN", 14, True, "content_gtin"),
        "10": ("BATCH/LOT", None, False, "batch_lot"),
        "11": ("PROD DATE", 6, True, "production_date"),
        "12": ("DUE DATE", 6, True, "due_date"),
        "13": ("PACK DATE", 6, True, "pack_date"),
        "15": ("BEST BEFORE", 6, True, "best_before"),
        "16": ("SELL BY", 6, True, "sell_by"),
        "17": ("USE BY", 6, True, "use_by"),
        "20": ("VARIANT", 2, True, "variant"),
        "21": ("SERIAL", None, False, "serial"),
        "22": ("CPV", None, False, "cpv"),
        "240": ("ADDITIONAL ID", None, False, "additional_id"),
        "241": ("CUSTOMER PART No", None, False, "customer_part_no"),
        "242": ("MTO VARIANT", None, False, "mto_variant"),
        "243": ("PCN", None, False, "pcn"),
        "250": ("SECONDARY SERIAL", None, False, "secondary_serial"),
        "30": ("COUNT", None, False, "count"),
        "310": ("NET WEIGHT (kg)", 6, True, "net_weight_kg"),
        "311": ("LENGTH (m)", 6, True, "length_m"),
        "312": ("WIDTH (m)", 6, True, "width_m"),
        "313": ("HEIGHT (m)", 6, True, "height_m"),
        "314": ("AREA (m²)", 6, True, "area_sqm"),
        "315": ("NET VOLUME (l)", 6, True, "net_volume_l"),
        "316": ("NET VOLUME (m³)", 6, True, "net_volume_cubic_m"),
        "320": ("NET WEIGHT (lb)", 6, True, "net_weight_lb"),
        "37": ("COUNT", None, False, "item_count"),
        "390": ("AMOUNT", None, False, "amount"),
        "392": ("PRICE", None, False, "price"),
        "393": ("PRICE ISO", None, False, "price_iso"),
        "400": ("ORDER NUMBER", None, False, "order_number"),
        "401": ("CONSIGNMENT", None, False, "consignment"),
        "402": ("SHIPMENT ID", 17, True, "shipment_id"),
        "403": ("ROUTE", None, False, "route"),
        "410": ("SHIP TO LOC", 13, True, "ship_to_loc"),
        "411": ("BILL TO", 13, True, "bill_to"),
        "412": ("PURCHASE FROM", 13, True, "purchase_from"),
        "413": ("SHIP FOR LOC", 13, True, "ship_for_loc"),
        "414": ("LOC No", 13, True, "loc_no"),
        "415": ("PAY TO", 13, True, "pay_to"),
        "420": ("SHIP TO POST", None, False, "ship_to_post"),
        "421": ("SHIP TO POST", None, False, "ship_to_post_with_iso"),
        "422": ("ORIGIN", 3, True, "origin"),
        "423": ("COUNTRY INITIAL PROCESS", None, False, "country_initial_process"),
        "424": ("COUNTRY PROCESS", 3, True, "country_process"),
        "425": ("COUNTRY DISASSEMBLY", 3, True, "country_disassembly"),
        "426": ("COUNTRY FULL PROCESS", 3, True, "country_full_process"),
        "7001": ("NSN", 13, True, "nsn"),
        "7002": ("MEAT CUT", None, False, "meat_cut"),
        "7003": ("EXPIRY TIME", 10, True, "expiry_time"),
        "7004": ("ACTIVE POTENCY", None, False, "active_potency"),
        "8001": ("DIMENSIONS", 14, True, "dimensions"),
        "8002": ("CMT No", None, False, "cmt_no"),
        "8003": ("GRAI", None, False, "grai"),
        "8004": ("GIAI", None, False, "giai"),
        "8005": ("PRICE PER UNIT", 6, True, "price_per_unit"),
        "8006": ("ITIP", 18, True, "itip"),
        "8007": ("IBAN", None, False, "iban"),
        "8008": ("PROD TIME", 12, True, "prod_time"),
        "8018": ("GSRN - RECIPIENT", 18, True, "gsrn_recipient"),
        "8020": ("REF No", None, False, "ref_no"),
        "8100": ("CID", None, False, "cid"),
        "8102": ("COUPON", None, False, "coupon"),
        "8110": ("POINTS", None, False, "points"),
        "8200": ("PRODUCT URL", None, False, "product_url"),
        "90": ("INTERNAL", None, False, "internal_1"),
        "91": ("INTERNAL", None, False, "internal_2"),
        "92": ("INTERNAL", None, False, "internal_3"),
        "93": ("INTERNAL", None, False, "internal_4"),
        "94": ("INTERNAL", None, False, "internal_5"),
        "95": ("INTERNAL", None, False, "internal_6"),
        "96": ("INTERNAL", None, False, "internal_7"),
        "97": ("INTERNAL", None, False, "internal_8"),
        "98": ("INTERNAL", None, False, "internal_9"),
        "99": ("INTERNAL", None, False, "internal_0"),
    }

    # Function-Code-1 (FNC1) character
    # In GS1-128, FNC1 is used as a separator for variable-length AIs
    # In plain text, it can be represented as a Group Separator (GS) character or "]C1"
    FNC1 = chr(29)  # ASCII 29, Group Separator

    # Type hints for common attributes for IDE completion
    # PyCharm will recognize these and provide code completion
    sscc: Optional[str] = None
    gtin: Optional[str] = None
    content_gtin: Optional[str] = None
    batch_lot: Optional[str] = None
    production_date: Optional[str] = None
    due_date: Optional[str] = None
    pack_date: Optional[str] = None
    best_before: Optional[str] = None
    sell_by: Optional[str] = None
    use_by: Optional[str] = None
    variant: Optional[str] = None
    serial: Optional[str] = None
    net_weight_kg: Optional[str] = None
    length_m: Optional[str] = None
    width_m: Optional[str] = None
    height_m: Optional[str] = None
    order_number: Optional[str] = None

    def __init__(self, barcode_data: str):
        """
        Initialize a Barcode object by decoding the barcode data.

        Args:
            barcode_data: The GS1 barcode string to decode
        """
        self.raw_barcode: str = barcode_data
        self.original_barcode: str = barcode_data
        self._data: Dict[str, Dict[str, Any]] = {}  # Internal data store

        # Decode the barcode and create attributes
        self._decode_barcode(barcode_data)

    def __str__(self) -> str:
        """String representation of the barcode"""
        return f"GS1 Barcode: {self.raw_barcode}"

    def __repr__(self) -> str:
        """Detailed representation of the barcode"""
        return f"Barcode({self.raw_barcode!r})"

    def __getattr__(self, name: str) -> Optional[str]:
        """Handle attribute access for properties not explicitly defined"""
        # Check if this is a known attribute that we haven't populated yet
        for ai, (_, _, _, attr_name) in self.AI_DEFINITIONS.items():
            if name == attr_name and ai not in self._data:
                # Return None for missing attributes
                return None

        # If not a known attribute, raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @staticmethod
    def _format_date(date_str: str) -> str:
        """Format a date string from YYMMDD to YYYY-MM-DD"""
        if len(date_str) != 6:
            return date_str

        try:
            year = 2000 + int(date_str[0:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])

            # Validate date
            if month < 1 or month > 12 or day < 1 or day > 31:
                return date_str

            return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            return date_str

    def _find_ai_length(self, barcode: str, start_pos: int) -> tuple[Optional[str], int]:
        """
        Find the length of the AI starting at start_pos.
        Returns the AI and its length.
        """
        # Check first 2 digits
        if start_pos + 2 > len(barcode):
            return None, 0

        ai_2 = barcode[start_pos:start_pos + 2]

        # Check if it's a 2-digit AI
        if ai_2 in self.AI_DEFINITIONS:
            return ai_2, 2

        # Check if it's a 3-digit AI
        if start_pos + 3 > len(barcode):
            return None, 0

        ai_3 = barcode[start_pos:start_pos + 3]
        if ai_3 in self.AI_DEFINITIONS:
            return ai_3, 3

        # Check if it's a 4-digit AI
        if start_pos + 4 > len(barcode):
            return None, 0

        ai_4 = barcode[start_pos:start_pos + 4]
        if ai_4 in self.AI_DEFINITIONS:
            return ai_4, 4

        # If no match found, assume it's a 2-digit AI (even if unknown)
        return ai_2, 2

    def _get_ai_data_length(self, ai: str, barcode: str, start_pos: int) -> int:
        """
        Determine the length of data for a given AI.
        For fixed-length AIs, return the defined length.
        For variable-length AIs, search for the next FNC1 or the end of data.
        """
        if ai in self.AI_DEFINITIONS:
            name, length, is_fixed, _ = self.AI_DEFINITIONS[ai]

            if is_fixed and length is not None:
                return length

        # For variable length, find next FNC1 or end of data
        next_fnc1 = barcode.find(self.FNC1, start_pos)

        # If no FNC1 found, use remaining data
        if next_fnc1 == -1:
            return len(barcode) - start_pos

        return next_fnc1 - start_pos

    def _decode_barcode(self, barcode: str) -> None:
        """
        Decode a GS1 barcode string and create attributes.
        """
        # Replace common FNC1 representations
        # Explicit "FNC1" text, "]C1", or ASCII 29 (Group Separator)
        barcode = barcode.replace("FNC1", self.FNC1).replace("]C1", self.FNC1).replace("\\x1d", self.FNC1)

        # Ensure barcode is a string
        if not isinstance(barcode, str):
            barcode = str(barcode)

        # Handle FNC1 at the start of the barcode (if present)
        if barcode.startswith(self.FNC1):
            barcode = barcode[1:]  # Remove initial FNC1

        pos = 0

        while pos < len(barcode):
            # Find AI
            ai, ai_length = self._find_ai_length(barcode, pos)

            if ai is None:
                # Cannot identify AI, skip to next position
                pos += 1
                continue

            pos += ai_length

            # Get length of data for this AI
            data_length = self._get_ai_data_length(ai, barcode, pos)

            # Extract data
            if pos + data_length <= len(barcode):
                data = barcode[pos:pos + data_length]

                # Format date fields
                if ai in ("11", "12", "13", "15", "16", "17"):
                    data = self._format_date(data)

                # Get AI name and attribute name
                if ai in self.AI_DEFINITIONS:
                    ai_name, _, _, attr_name = self.AI_DEFINITIONS[ai]
                else:
                    ai_name = f"Unknown AI ({ai})"
                    attr_name = f"unknown_{ai}"

                # Store in internal data structure
                self._data[ai] = {
                    "ai": ai,
                    "name": ai_name,
                    "data": data,
                    "attr_name": attr_name
                }

                # Set as attribute on the object
                setattr(self, attr_name, data)

            # Move to next AI
            pos += data_length

            # Skip FNC1 separator if present
            if pos < len(barcode) and barcode[pos] == self.FNC1:
                pos += 1

    def as_dict(self) -> Dict[str, str]:
        """
        Return a dictionary of all decoded data.

        Returns:
            Dictionary with attribute names as keys and values as values
        """
        result = {}

        for ai_data in self._data.values():
            result[ai_data["attr_name"]] = ai_data["data"]

        return result

    def as_json(self, indent: int = 2) -> str:
        """
        Return all decoded data as a JSON string.

        Args:
            indent: Number of spaces for JSON indentation

        Returns:
            JSON string representation of the barcode data
        """
        return json.dumps(self.as_dict(), indent=indent)

    def get_ai_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Return the raw AI dictionary with all detailed information.

        Returns:
            Dictionary with AI codes as keys and detailed info as values
        """
        return self._data.copy()