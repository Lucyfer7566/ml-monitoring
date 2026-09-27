route:
  receiver: 'telegram'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 1m
  repeat_interval: 1h

receivers:
- name: 'telegram'
  telegram_configs:
  - bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: ${TELEGRAM_CHAT_ID}
    api_url: "https://api.telegram.org"
    parse_mode: "HTML"
    message: |-
      {{ range .Alerts }}
      <b>🚨 ALERT: {{ .Labels.alertname }}</b>
      <b>Severity:</b> {{ .Labels.severity }}
      <b>Component:</b> {{ .Labels.component }}
      
      <b>Description:</b> {{ .Annotations.description }}
      <b>Summary:</b> {{ .Annotations.summary }}
      {{ if .Annotations.dashboard }}
      <b>Dashboard:</b> <a href="{{ .Annotations.dashboard }}">View in Grafana</a>
      {{ end }}
      {{ if .Annotations.runbook }}
      <b>Action:</b> {{ .Annotations.runbook }}
      {{ end }}
      {{ end }}
