import sys
import json
import logging
import idna
import requests
import os

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class InfomaniakAPI:
    base_url = "https://api.infomaniak.com"

    def __init__(self, token):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _get_request(self, url, params=None):
        url = self.base_url + url
        logger.debug("GET %s", url)
        with self.session.get(url, params=params) as response:
            response.raise_for_status()
            result = response.json()
            if result.get("result") == "success":
                return result.get("data")
            else:
                raise Exception(f"Error in API request: {result}")

    def _post_request(self, url, data):
        url = self.base_url + url
        logger.debug("POST %s", url)
        with self.session.post(url, data=data) as response:
            response.raise_for_status()
            result = response.json()
            if result.get("result") == "success":
                return result.get("data")
            else:
                raise Exception(f"Error in API request: {result}")

    def _delete_request(self, url):
        url = self.base_url + url
        logger.debug("DELETE %s", url)
        with self.session.delete(url) as response:
            response.raise_for_status()
            result = response.json()
            if result.get("result") == "success":
                return result.get("data")
            else:
                raise Exception(f"Error in API request: {result}")

    def _find_zone(self, domain):
        while "." in domain:
            result = self._get_request(f"/1/product?service_name=domain&customer_name={domain}")
            if len(result) == 1:
                return result[0]["id"], domain
            domain = domain.split('.', 1)[1]
        raise Exception("Domain not found")

    def _get_records(self, domain_id):
        return self._get_request(f"/1/domain/{domain_id}/dns/record")

    def add_a_record(self, domain, source, target, ttl=3600):
        logger.debug("add_a_record %s %s %s", domain, source, target)
        domain_id, domain_name = self._find_zone(domain)
        relative_source = "" if source in ("", ".") else source
        data = {"type": "A", "source": relative_source, "target": target, "ttl": ttl}
        self._post_request(f"/1/domain/{domain_id}/dns/record", data)

    def del_a_record(self, domain, source, target):
        logger.debug("del_a_record %s %s %s", domain, source, target)
        domain_id, domain_name = self._find_zone(domain)
        relative_source = "" if source in ("", ".") else source
        records = self._get_records(domain_id)
        logger.debug("Fetched records: %s", json.dumps(records, indent=2))

        # Normalize the source for matching
        def normalize_source(record_source):
            if record_source in ("", "."):
                return domain_name
            return f"{record_source}.{domain_name}" if not record_source.endswith(domain_name) else record_source

        matching_records = [
            record for record in records
            if record["type"] == "A" and normalize_source(record["source"]) == f"{source}.{domain_name}" and record["target"] == target
        ]

        if not matching_records:
            raise Exception("A record not found")
        if len(matching_records) > 1:
            raise Exception("Multiple matching A records found")
        record_id = matching_records[0]["id"]
        self._delete_request(f"/1/domain/{domain_id}/dns/record/{record_id}")

    def update_a_record(self, domain, source, old_target, new_target, ttl=3600):
        logger.debug("update_a_record %s %s %s %s", domain, source, old_target, new_target)
        self.del_a_record(domain, source, old_target)
        self.add_a_record(domain, source, new_target, ttl)

def main():
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print("Usage: manage_a_records.py <domain> <source> <target> <add|delete|update> [new_target]")
        sys.exit(1)

    domain, source, target, action = sys.argv[1:5]
    new_target = sys.argv[5] if len(sys.argv) == 6 else None

    token = os.getenv("INFOMANIAK_API_TOKEN")
    if not token:
        print("Error: INFOMANIAK_API_TOKEN environment variable not set.")
        sys.exit(1)

    api = InfomaniakAPI(token)

    try:
        if action == "add":
            api.add_a_record(domain, source, target)
            print(f"A record added: {source} -> {target}")
        elif action == "delete":
            api.del_a_record(domain, source, target)
            print(f"A record deleted: {source} -> {target}")
        elif action == "update":
            if not new_target:
                print("Error: 'update' action requires a new_target argument.")
                sys.exit(1)
            api.update_a_record(domain, source, target, new_target)
            print(f"A record updated: {source} -> {target} to {new_target}")
        else:
            print("Invalid action. Use 'add', 'delete', or 'update'.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
