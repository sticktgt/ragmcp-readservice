{{- define "common.helm-labels" -}}
app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
app.kubernetes.io/revision: {{ .Release.Revision | quote }}
app.dognauts/subjectArea: {{ .Values.subjectArea }}
{{- end -}}
{{- define "readservice.flattenEnv" -}}
{{- $env := . -}}
{{- range $name, $item := $env }}
  {{- $key := (printf "RS__%s" (upper (replace "-" "_" $name))) -}}
  {{- if kindIs "map" $item }}
    {{- range $subname, $subitem := $item }}
      {{- $subkey := (printf "%s__%s" $key (upper (replace "-" "_" $subname))) -}}
      {{- if kindIs "map" $subitem }}
        {{- range $subsubname, $subsubitem := $subitem }}
          {{- $subsubkey := (printf "%s__%s" $subkey (upper (replace "-" "_" $subsubname))) -}}
          {{- include "readservice.flattenEnvItem" (dict "name" $subsubkey "item" $subsubitem) }}
        {{- end }}
      {{- else }}
        {{- include "readservice.flattenEnvItem" (dict "name" $subkey "item" $subitem) }}
      {{- end }}
    {{- end }}
  {{- else }}
    {{- include "readservice.flattenEnvItem" (dict "name" $key "item" $item) }}
  {{- end }}
{{- end }}
{{- end }}

{{- define "readservice.flattenEnvItem" -}}
{{- $name := .name -}}
{{- $item := .item -}}
{{- if kindIs "map" $item }}
  {{- if hasKey $item "value" }}
- name: {{ $name }}
  value: {{ $item.value | quote }}
  {{- else if hasKey $item "valueFrom" }}
- name: {{ $name }}
  valueFrom:
    secretKeyRef:
      name: {{ $item.valueFrom.secretKeyRef.name }}
      key: {{ $item.valueFrom.secretKeyRef.key }}
  {{- end }}
{{- else if or (kindIs "string" $item) (kindIs "bool" $item) (kindIs "int" $item) (kindIs "float64" $item) }}
- name: {{ $name }}
  value: {{ $item | quote }}
{{- end }}
{{- end }}
