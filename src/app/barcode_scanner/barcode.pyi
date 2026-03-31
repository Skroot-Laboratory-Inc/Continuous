from typing import Dict, Optional, Any, Union


class Barcode:
    raw_barcode: str
    original_barcode: str
    _data: Dict[str, Dict[str, Any]]

    # Common GS1 attributes
    sscc: Optional[str]
    gtin: Optional[str]
    content_gtin: Optional[str]
    batch_lot: Optional[str]
    production_date: Optional[str]
    due_date: Optional[str]
    pack_date: Optional[str]
    best_before: Optional[str]
    sell_by: Optional[str]
    use_by: Optional[str]
    variant: Optional[str]
    serial: Optional[str]
    cpv: Optional[str]
    additional_id: Optional[str]
    customer_part_no: Optional[str]
    mto_variant: Optional[str]
    pcn: Optional[str]
    secondary_serial: Optional[str]
    count: Optional[str]
    net_weight_kg: Optional[str]
    length_m: Optional[str]
    width_m: Optional[str]
    height_m: Optional[str]
    area_sqm: Optional[str]
    net_volume_l: Optional[str]
    net_volume_cubic_m: Optional[str]
    net_weight_lb: Optional[str]
    item_count: Optional[str]
    amount: Optional[str]
    price: Optional[str]
    price_iso: Optional[str]
    order_number: Optional[str]
    consignment: Optional[str]
    shipment_id: Optional[str]
    route: Optional[str]
    ship_to_loc: Optional[str]
    bill_to: Optional[str]
    purchase_from: Optional[str]
    ship_for_loc: Optional[str]
    loc_no: Optional[str]
    pay_to: Optional[str]
    ship_to_post: Optional[str]
    ship_to_post_with_iso: Optional[str]
    origin: Optional[str]
    country_initial_process: Optional[str]
    country_process: Optional[str]
    country_disassembly: Optional[str]
    country_full_process: Optional[str]
    nsn: Optional[str]
    meat_cut: Optional[str]
    expiry_time: Optional[str]
    active_potency: Optional[str]
    dimensions: Optional[str]
    cmt_no: Optional[str]
    grai: Optional[str]
    giai: Optional[str]
    price_per_unit: Optional[str]
    itip: Optional[str]
    iban: Optional[str]
    prod_time: Optional[str]
    gsrn_recipient: Optional[str]
    ref_no: Optional[str]
    cid: Optional[str]
    coupon: Optional[str]
    points: Optional[str]
    product_url: Optional[str]
    internal_1: Optional[str]
    internal_2: Optional[str]
    internal_3: Optional[str]
    internal_4: Optional[str]
    internal_5: Optional[str]
    internal_6: Optional[str]
    internal_7: Optional[str]
    internal_8: Optional[str]
    internal_9: Optional[str]
    internal_0: Optional[str]

    def __init__(self, barcode_data: str) -> None: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def as_dict(self) -> Dict[str, str]: ...

    def as_json(self, indent: int = 2) -> str: ...

    def get_ai_dict(self) -> Dict[str, Dict[str, Any]]: ...