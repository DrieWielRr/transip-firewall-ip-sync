# transip-firewall-ip-sync

Docker service that monitors a dynamic public IP address and synchronizes TransIP VPS firewall rules through the API.

## Environment variables

| Variable                   | Default                           | Description                                                   |
| -------------------------- | --------------------------------- | ------------------------------------------------------------- |
| `IP_CHECK_INTERVAL`        | `30`                              | Seconds between public IP checks                              |
| `TRANSIP_UPDATE_COOLDOWN`  | `300`                             | Minimum time between TransIP firewall updates                 |
| `TRANSIP_ACCOUNT_NAME`     | `-`                               | TransIP account name                                          |
| `TRANSIP_VPS_NAME`         | `-`                               | Name of the TransIP VPS to update firewall rules              |
| `TRANSIP_PRIVATE_KEY_FILE` | `/config/transip_private_key.pem` | Path to the TransIP API private key file inside the container |
| `TRANSIP_FIREWALL_RULES`   | `[]`                              | JSON array containing firewall rule descriptions to update    |

### Example

```yaml
environment:
  IP_CHECK_INTERVAL: 30
  TRANSIP_UPDATE_COOLDOWN: 300
  TRANSIP_ACCOUNT_NAME: myaccount
  TRANSIP_VPS_NAME: my-vps-name
  TRANSIP_PRIVATE_KEY_FILE: /config/transip_private_key.pem
  TRANSIP_FIREWALL_RULES: '["WireGuard","Portainer Agent","SSH"]'
```

The firewall rule descriptions must exactly match the `description` field of the TransIP VPS firewall rules.


## Storage

Mount:
/data

The service stores its state in:
/data/state.json