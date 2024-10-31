# Lake Formation permissions

#<AccountId> - Replace with accountId
#<SecurityLakeAccountId> - Replace with SecurityLake AccountId

```
aws lakeformation grant-permissions --principal DataLakePrincipalIdentifier=arn:aws:iam::<AccountId>:role/EmbeddingProcessorTaskExecutionRole --permissions "SELECT" --resource '{ "Table": {"CatalogId":"<SecurityLakeAccountId>", "DatabaseName":"amazon_security_lake_glue_db_us_east_1", "Name":"amazon_security_lake_table_us_east_1_sh_findings_2_0"}}'

aws lakeformation grant-permissions --principal DataLakePrincipalIdentifier=arn:aws:iam::<AccountId>:role/EmbeddingProcessorTaskExecutionRole --permissions "SELECT" --resource '{ "Table": {"CatalogId":"<SecurityLakeAccountId>", "DatabaseName":"amazon_security_lake_glue_db_us_east_1", "Name":"amazon_security_lake_table_us_east_1_route53_2_0"}}'

aws lakeformation grant-permissions --principal DataLakePrincipalIdentifier=arn:aws:iam::<AccountId>:role/EmbeddingProcessorTaskExecutionRole --permissions "SELECT" --resource '{ "Table": {"CatalogId":"<SecurityLakeAccountId>", "DatabaseName":"amazon_security_lake_glue_db_us_east_1", "Name":"amazon_security_lake_table_us_east_1_s3_data_2_0"}}'

aws lakeformation grant-permissions --principal DataLakePrincipalIdentifier=arn:aws:iam::<AccountId>:role/EmbeddingProcessorTaskExecutionRole --permissions "SELECT" --resource '{ "Table": {"CatalogId":"<SecurityLakeAccountId>", "DatabaseName":"amazon_security_lake_glue_db_us_east_1", "Name":"amazon_security_lake_table_us_east_1_vpc_flow_2_0"}}'

aws lakeformation grant-permissions --principal DataLakePrincipalIdentifier=arn:aws:iam::<AccountId>:role/EmbeddingProcessorTaskExecutionRole --permissions "SELECT" --resource '{ "Table": {"CatalogId":"<SecurityLakeAccountId>", "DatabaseName":"amazon_security_lake_glue_db_us_east_1", "Name":"amazon_security_lake_table_us_east_1_cloud_trail_mgmt_2_0"}}'

aws lakeformation grant-permissions --principal DataLakePrincipalIdentifier=arn:aws:iam::<AccountId>:role/EmbeddingProcessorTaskExecutionRole --permissions "SELECT" --resource '{ "Table": {"CatalogId":"<SecurityLakeAccountId>", "DatabaseName":"amazon_security_lake_glue_db_us_east_1", "Name":"amazon_security_lake_table_us_east_1_lambda_execution_2_0"}}'

aws lakeformation grant-permissions \
 --principal DataLakePrincipalIdentifier=arn:aws:iam::<AccountId>:role/EmbeddingProcessorTaskExecutionRole \
 --permissions "SELECT" "DESCRIBE" \
 --resource '{ "Table": { "CatalogId":"<AccountId>", "DatabaseName":"amazon_security_lake_glue_db_us_east_1", "TableWildcard":{} }}'
```