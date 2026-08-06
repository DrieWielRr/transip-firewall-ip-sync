# transip-firewall-ip-sync

Docker service that monitors a dynamic public IP address and synchronizes TransIP VPS firewall rules through the API.

## Environment variables

| Variable | Default | Description |
|---|---|---|
| IP_CHECK_INTERVAL | 30 | Seconds between IP checks |
| TRANSIP_UPDATE_COOLDOWN | 300 | Minimum time between TransIP updates |

## Storage

Mount:
/data

The service stores its state in:
/data/state.json