
import os

import httpx


class UrjaPortalClient:
    def __init__(self):
        self.base_url = "https://urja-ops.flockenergy.tech"
        self.session_cookie = os.getenv("URJA_SESSION_COOKIE")

    def get_meters(self, page: int = 1, query: str = "") -> dict:
        if not self.session_cookie:
            raise RuntimeError(
                "URJA_SESSION_COOKIE is missing from your .env configuration"
            )

        url = f"{self.base_url}/portal/meters/search"

        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url,
                params={"q": query, "page": page},
                cookies={
                    "__Secure-better-auth.session_token": self.session_cookie
                },
            )
            response.raise_for_status()
            return response.json()
    
    def get_meter_details(self, meter_id: str) -> dict:
        if not self.session_cookie:
            raise RuntimeError(
                "URJA_SESSION_COOKIE is missing from your .env configuration"
            )

        url = f"{self.base_url}/meters/{meter_id}/__data.json"

        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url,
                cookies={
                    "__Secure-better-auth.session_token": self.session_cookie
                },
            )
            response.raise_for_status()
            return self.normalize_meter_details(response.json())

        

    def normalize_meter_details(self, response_data: dict) -> dict:
        nodes = response_data.get("nodes", [])

        meter_node = next(
            (
                node for node in nodes
                if isinstance(node, dict)
                and isinstance(node.get("data"), list)
                and node.get("uses", {}).get("params") == ["id"]
            ),
            None,
        )

        if not meter_node:
            raise ValueError("Could not find meter details in portal response")

        data = meter_node["data"]

        # Resolve SvelteKit's numeric references recursively.
        def resolve(value, seen=None):
            if seen is None:
                seen = set()

            if isinstance(value, int) and not isinstance(value, bool):
                if value < 0 or value >= len(data) or value in seen:
                    return value
                return resolve(data[value], seen | {value})

            if isinstance(value, list):
                return [resolve(item, seen.copy()) for item in value]

            if isinstance(value, dict):
                return {
                    key: resolve(item, seen.copy())
                    for key, item in value.items()
                }

            return value

        root = data[0]
        meter_id = resolve(root.get("meterId"))
        detail = resolve(root.get("detail"))
        hierarchy = resolve(root.get("hierarchy"))

        # Convert parameter objects into a readable dictionary.
        parameters = {}
        if isinstance(detail, dict):
            parameter_items = detail.get("data", [])
            if isinstance(parameter_items, list):
                for item in parameter_items:
                    if isinstance(item, dict):
                        name = item.get("parameterName")
                        value = item.get("parameterValue")
                        if name is not None:
                            parameters[name] = value

        # Normalize the hierarchy labels.
        hierarchy_fields = {
            "zone": "Zone",
            "circle": "Circle",
            "division": "Division",
            "subdivision": "Subdivision",
            "substation": "Sub Station",
            "feeder": "Feeder",
            "transformer": "DT",
        }

        normalized_hierarchy = {}
        if isinstance(hierarchy, dict):
            normalized_hierarchy = {
                key: hierarchy[label]
                for key, label in hierarchy_fields.items()
                if label in hierarchy
            }

        return {
            "meter_id": meter_id,
            "serial_number": parameters.get("Serial No"),
            "make": parameters.get("Make"),
            "phase_type": parameters.get("Phase Type"),
            "installation_status": parameters.get("Installation Status"),
            "installation_type": parameters.get("Installation Type"),
            "hierarchy": normalized_hierarchy,
        }


    
    def get_meter_geo(self, meter_id: str) -> dict:
        if not self.session_cookie:
            raise RuntimeError(
                "URJA_SESSION_COOKIE is missing from your .env configuration"
            )

        url = f"{self.base_url}/portal/meters/{meter_id}/geo"

        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url,
                cookies={
                    "__Secure-better-auth.session_token": self.session_cookie
                },
            )
            response.raise_for_status()
            result = response.json()

        coordinates = result.get("data", {})

        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")

        if latitude is None or longitude is None:
            raise ValueError("Portal response did not contain coordinates")

        return {
            "meter_id": meter_id,
            "latitude": float(latitude),
            "longitude": float(longitude),
        }



    def get_meter_energy(self, meter_id: str) -> dict:
        if not self.session_cookie:
            raise RuntimeError(
                "URJA_SESSION_COOKIE is missing from your .env configuration"
            )

        url = f"{self.base_url}/portal/meters/{meter_id}/energy"

        with httpx.Client(timeout=15.0) as client:
            response = client.get(
                url,
                cookies={
                    "__Secure-better-auth.session_token": self.session_cookie
                },
            )
            response.raise_for_status()
            result = response.json()

        # The portal returns readings as a list of records.
        # Handle either a direct list or a {"data": [...]} response.
        readings = result.get("data", []) if isinstance(result, dict) else result

        if not isinstance(readings, list):
            raise ValueError("Unexpected energy response format")

        normalized_readings = []
        for item in readings:
            if not isinstance(item, dict):
                continue

            normalized_readings.append({
                "timestamp": item.get("timestamp"),
                "kwh": float(item["kwh"]) if item.get("kwh") is not None else None,
                "kvah": float(item["kvah"]) if item.get("kvah") is not None else None,
                "voltage_r": float(item["voltR"]) if item.get("voltR") is not None else None,
            })

        return {
            "meter_id": meter_id,
            "readings": normalized_readings,
            "count": len(normalized_readings),
        }


