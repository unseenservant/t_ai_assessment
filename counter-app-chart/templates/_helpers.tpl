{{/*
Expand the name of the chart.
*/}}
{{- define "counter-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "counter-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "counter-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "counter-app.labels" -}}
helm.sh/chart: {{ include "counter-app.chart" . }}
{{ include "counter-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "counter-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "counter-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Flask app labels
*/}}
{{- define "counter-app.flaskLabels" -}}
app: {{ .Values.app.name }}
{{- end }}

{{/*
Flask app selector labels
*/}}
{{- define "counter-app.flaskSelectorLabels" -}}
app: {{ .Values.app.name }}
{{- end }}

{{/*
Postgres labels
*/}}
{{- define "counter-app.postgresLabels" -}}
app: {{ .Values.postgres.name }}
{{- end }}

{{/*
Postgres selector labels
*/}}
{{- define "counter-app.postgresSelectorLabels" -}}
app: {{ .Values.postgres.name }}
{{- end }}
