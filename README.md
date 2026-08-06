# transip-firewall-ip-sync

Docker service that monitors a dynamic public IP address and synchronizes TransIP VPS firewall rules through the API.

## Environment variables

| Variable                    | Default | Description                                      |
| --------------------------- | ------- | ------------------------------------------------ |
| IP_CHECK_INTERVAL            | 30      | Seconds between public IP checks                 |
| TRANSIP_UPDATE_COOLDOWN      | 300     | Minimum time between TransIP firewall updates    |
| TRANSIP_ACCOUNT_NAME         | -       | TransIP account name                             |
| TRANSIP_PRIVATE_KEY          | -       | TransIP API private key                          |
| TRANSIP_VPS_NAME             | -       | Name of the TransIP VPS to update firewall rules |

## Storage

Mount:
/data

The service stores its state in:
/data/state.json