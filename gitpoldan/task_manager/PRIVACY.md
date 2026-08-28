# Privacy Policy — Transit Task Manager

## Data this plugin processes

- **Task data you send**: tenant identifiers, task titles, descriptions,
  payloads, tags, statuses, TTL values and status metadata provided in tool
  calls.
- **S3 / MinIO credentials**: endpoint, access key id, secret access key and
  bucket configured on the tool provider. These are handled by the Dify runtime
  and used only to connect to the object store you specify.

## Where data is stored

All task data is written to **your own S3 / MinIO bucket**, as one SQLite
database per tenant (`{prefix}/{namespace?}/{tenant}.sqlite`) plus a transient
lock object (`{tenant}.lock`). The plugin keeps no other copy: databases are
pulled into a temporary file for the duration of a single tool call and removed
afterwards.

## Data sharing

The plugin does not transmit your data to the plugin author or any third party.
Data flows only between the Dify host and the object storage endpoint you
configure.

## Retention and deletion

Retention is entirely under your control. Use `delete_task` (hard delete) to
remove records, or delete the tenant database object directly in your bucket.

## Contact

Author: **gitpoldan**. Questions: bv2020donch@gmail.com
