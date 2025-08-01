{{- define "readservice.flattenEnv" -}}
{{- range $k, $v := . }}
{{- include "readservice.flattenEnvItem" (dict "prefix" (upper $k) "value" $v) }}
{{- end }}
{{- end }}

{{- define "readservice.flattenEnvItem" -}}
{{- $prefix := .prefix }}
{{- $value := .value }}

{{- if and (kindIs "map" $value) (or (hasKey $value "value") (hasKey $value "valueFrom")) }}
- name: RS__{{ $prefix }}
{{- if hasKey $value "value" }}
  value: {{ $value.value | quote }}
{{- else if hasKey $value "valueFrom" }}
  valueFrom:
    secretKeyRef:
      name: {{ $value.valueFrom.secretKeyRef.name }}
      key: {{ $value.valueFrom.secretKeyRef.key }}
{{- end }}
{{- else if kindIs "map" $value }}
{{- range $k, $v := $value }}
{{- include "readservice.flattenEnvItem" (dict "prefix" (printf "%s__%s" $prefix (upper $k)) "value" $v) }}
{{- end }}
{{- end }}
{{- end }}

