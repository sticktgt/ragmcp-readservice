{{- define "common.helm-labels" -}}
app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
app.kubernetes.io/revision: {{ .Release.Revision | quote }}
app.dognauts/subjectArea: {{ .Values.subjectArea }}
{{- end -}}
{{- define "readservice.flattenEnv" -}}
{{- $env := . -}}
{{- range $name, $item := $env -}}
  {{- $key := (printf "RS__%s" (upper (replace "-" "_" $name))) -}}
  {{- include "readservice.flattenEnvItem" (dict "name" $key "item" $item) }}
{{- end -}}
{{- end -}}

{{- define "readservice.flattenEnvItem" -}}
{{- $name := .name -}}
{{- $item := .item -}}

{{- if kindIs "map" $item -}}
  {{- if or (hasKey $item "value") (hasKey $item "valueFrom") -}}
    {{- if hasKey $item "value" -}}
{{- printf "\n" -}}- name: {{ $name }}
  value: {{ $item.value | quote }}
    {{- else if hasKey $item "valueFrom" -}}
{{- printf "\n" -}}- name: {{ $name }}
  valueFrom:
    {{- if hasKey $item.valueFrom "secretKeyRef" }}
    secretKeyRef:
      name: {{ $item.valueFrom.secretKeyRef.name }}
      key: {{ $item.valueFrom.secretKeyRef.key }}
    {{- end }}
    {{- if hasKey $item.valueFrom "configMapKeyRef" }}
    configMapKeyRef:
      name: {{ $item.valueFrom.configMapKeyRef.name }}
      key: {{ $item.valueFrom.configMapKeyRef.key }}
    {{- end }}
    {{- if hasKey $item.valueFrom "fieldRef" }}
    fieldRef:
      fieldPath: {{ $item.valueFrom.fieldRef.fieldPath }}
    {{- end }}
    {{- if hasKey $item.valueFrom "resourceFieldRef" }}
    resourceFieldRef:
      resource: {{ $item.valueFrom.resourceFieldRef.resource }}
    {{- end }}
    {{- /* add other valueFrom kinds if you need them */ -}}
    {{- end }}
  {{- else -}}
    {{- range $k, $v := $item -}}
      {{- $subname := printf "%s__%s" $name (upper (replace "-" "_" $k)) -}}
      {{- include "readservice.flattenEnvItem" (dict "name" $subname "item" $v) }}
    {{- end -}}
  {{- end -}}
{{- else if or (kindIs "string" $item) (kindIs "bool" $item) (kindIs "int" $item) (kindIs "float64" $item) -}}
{{- printf "\n" -}}- name: {{ $name }}
  value: {{ $item | quote }}
{{- end -}}
{{- end -}}
