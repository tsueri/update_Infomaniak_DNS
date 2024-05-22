# update_Infomaniak_DNS
This is a pythonscript to update A-Records via API on the Infomaniak nameserver.

The [Infomaniak AP](https://developer.infomaniak.com/docs/api)I is not documented to modify DNS-Records. So I created this one. Use at your own risk!

You need a API-Key from [here](https://manager.infomaniak.com/v3/ng/profile/user/token/list). Scope is DOMAIN.

### Usage

#### Add an A Record

```bash
python manage_dns_records.py <domain> <source> <target> add
```

Example for the root domain:

```bash
python manage_dns_records.py example.com . 123.124.125.126 add
```

Example for a subdomain:

```bash
python manage_dns_records.py example.com www 123.124.125.126 add
```

#### Delete an A Record

```bash
python manage_dns_records.py <domain> <source> <target> delete
```

Example for the root domain:

```bash
python manage_dns_records.py example.com . 123.124.125.126 delete
```

Example for a subdomain:

```bash
python manage_dns_records.py example.com www 123.124.125.126 delete
```


#### Update an A Record

```bash
python manage_dns_records.py <domain> <source> <old_target> update <new_target>
```

Example for the root domain:

```bash
python manage_dns_records.py example.com . 123.124.125.126 update 231.232.233.324
```

Example for a subdomain:

```bash
python manage_dns_records.py example.com www 123.124.125.126 update 231.232.233.324
```
