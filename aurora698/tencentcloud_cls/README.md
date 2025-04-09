# Tencent Cloud CLS Plugin for Dify  

## Overview  

The Tencent Cloud CLS (Cloud Log Service) Plugin enables seamless integration between Dify and Tencent Cloud's powerful log management service.  

## Features  

- ​**Secure Authentication**  
- ​**Flexible Querying** with CQL support  


## Configuration  

### Required Credentials:  
- SecretId  
- SecretKey  
- Default Region (e.g. ap-guangzhou)  
- Default Topic ID  

Get these from [Tencent Cloud CAM console](https://console.cloud.tencent.com/cam/capi).  

## Usage  

### Basic Query:  
```
status:404 | select count(*) as error_count
```

### Advanced Options:  
- Region override  
- TopicId override  
- Time Range (From/To timestamps)  
- Limit results (default: 20)  

## Examples  
1. Count 404 errors:  
```
status:404 | select count(*) as error_count
```
2. Find user activities:  
```
username:"john.doe" AND action:"login"
```

## Support  
[Tencent Cloud Online Support](https://cloud.tencent.com/online-service)  
