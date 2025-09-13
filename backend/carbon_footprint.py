def estimate_event_carbon_footprint(participants: int, transport_modes: dict) -> float:
    """
    Estimate carbon footprint in kg CO2 for an event.
    :param participants: Number of participants
    :param transport_modes: Dict of transport mode to average footprint per participant (kg CO2)
    :return: Estimated total carbon footprint in kg CO2
    """
    total_footprint = 0.0
    for mode, footprint_per_person in transport_modes.items():
        # Assume equal distribution among modes for simplicity
        total_footprint += participants * footprint_per_person / len(transport_modes)
    return total_footprint
