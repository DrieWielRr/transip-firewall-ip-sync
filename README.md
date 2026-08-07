# transip-firewall-ip-sync

Docker service that monitors a dynamic public IP address and synchronizes TransIP VPS firewall rules through the TransIP REST API.

## Environment variables

| Variable                   | Default                           | Description                                                    |
| -------------------------- | --------------------------------- | -------------------------------------------------------------- |
| `IP_CHECK_INTERVAL`        | `30`                              | Seconds between public IP checks                               |
| `TRANSIP_UPDATE_COOLDOWN`  | `300`                             | Minimum time between TransIP firewall updates                  |
| `TRANSIP_ACCOUNT_NAME`     | `-`                               | TransIP account name                                           |
| `TRANSIP_VPS_NAME`         | `-`                               | Name of the TransIP VPS to update firewall rules               |
| `TRANSIP_PRIVATE_KEY_FILE` | `/config/transip_private_key.pem` | Path **inside the container** to the TransIP API private key   |
| `TRANSIP_FIREWALL_RULES`   | `[]`                              | JSON array containing the firewall rule descriptions to update |

| `TRANSIP_UPDATE_DNS`       | `false`                           | Enable updating DNS A records in addition to firewall rules    |
| `TRANSIP_DNS_RECORDS`      | `{}`                              | JSON object mapping domains to DNS record names to update      |
| `TRANSIP_DNS_TTL`          | `300`                             | TTL (in seconds) to set on updated DNS records                 |

### Example

```yaml
environment:
  IP_CHECK_INTERVAL: 30
  TRANSIP_UPDATE_COOLDOWN: 300
  TRANSIP_ACCOUNT_NAME: myaccount
  TRANSIP_VPS_NAME: my-vps-name
  TRANSIP_PRIVATE_KEY_FILE: /config/transip_private_key.pem
  TRANSIP_FIREWALL_RULES: '["HTTP","HTTPS","SSH"]'
  TRANSIP_UPDATE_DNS: true
  TRANSIP_DNS_RECORDS: '{"example.com":["@","home","vpn"],"example2.com":["@","home"]}'
  TRANSIP_DNS_TTL: 300
```

The firewall rule descriptions must exactly match the `description` field of the corresponding TransIP VPS firewall rules.

## Private key

The TransIP API private key is loaded from a file mounted into the container.
The host directory containing the key is configured with:

```yaml
TRANSIP_CONFIG_PATH
```

By default:

```yaml
TRANSIP_CONFIG_PATH=./config
```

The container mounts this directory as:

```text
/config
```

The private key file path inside the container is configured with:

```yaml
TRANSIP_PRIVATE_KEY_FILE
```

Default:

```text
/config/transip_private_key.pem
```

Example host layout:

```text
.
├── config
│   └── transip_private_key.pem
└── data
    └── state.json
```

Example compose configuration:

```yaml
environment:
  TRANSIP_PRIVATE_KEY_FILE: /config/transip_private_key.pem

volumes:
  - ./config:/config:ro
```

The private key file should contain the TransIP Key Pair private key in PEM format. The file is mounted read-only because the service only needs to read it.

## Storage

The service stores runtime state in:

```text
/data/state.json
```

The host location can be configured with:

```yaml
TRANSIP_DATA_PATH
```

Default:

```yaml
TRANSIP_DATA_PATH=./data
```

Example:

```yaml
volumes:
  - /your/docker/path/data:/data
```

The state file contains:
* Last observed public IP
* Last detected IP change
* Last synchronization result
* Cached TransIP access token

```
```
