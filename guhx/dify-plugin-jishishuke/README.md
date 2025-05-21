## Jishishuke API Toolbox

**Author:** [guhx](https://github.com/billy723/dify-plugin-jishishuke)  
**Version:** 0.0.1  
**Type:** Tool

---

### About Us
Zhengzhou Jishi Digital Technology Co., Ltd. is a data service provider specializing in address-related data, integrating geospatial, cyberspace, and physical space. For the Dify platform, we provide tool plugins to call our API services, offering more features for your AI workflows.

---

### Features
* **Ipv4 Location Query - City** — Query the location of an IPv4 address with city-level accuracy. [Field Description](https://api.jishishuke.com/doc/44)
* **Ipv6 Location Query - City** — Query the location of an IPv6 address with city-level accuracy. [Field Description](https://api.jishishuke.com/doc/45)

---

### 🛠️Instructions for Use
1. Register at the [JishiShuke API Marketplace](https://api.jishishuke.com/)
2. After registration, log in and go to User Console - Key Management to generate and copy your API key
3. In the Dify platform's plugin management, add the plugin and enter your key and query parameters
4. Execute the query and continue your workflow

---

### Usage Examples
#### 📍 Ipv4 Location Query - City
![](_assets/v4city_1.png)
```json
{
    "code": 200,
    "data": {
    "asNumber": "4808",
    "cityCode": "110000",
    "cityName": "北京市",
    "continentCode": "AS",
    "continentName": "亚洲",
    "countryCode": "CN",
    "countryName": "中国",
    "ipAddress": "123.123.123.123",
    "isp": "中国联通",
    "latitude": "39.903313",
    "longitude": "116.71881",
    "provinceCode": "110000",
    "provinceName": "北京市",
    "timeZone": "UTC+08:00",
    "zipcode": "100000"
    },
    "exec_time": 0.084021,
    "ip": "你的访问ip",
    "msg": "操作成功"
}
```

#### 📍 Ipv6 Location Query - City

![](_assets/v6city_1.png)
```json
{
    "code": 200,
    "data": {
    "asNumber": "4134",
    "cityCode": "610100",
    "cityName": "西安市",
    "continentCode": "AS",
    "continentName": "亚洲",
    "countryCode": "CN",
    "countryName": "中国",
    "ipAddress": "240e:358:d4a:9900:4a1f:2dff:fe10:c52b",
    "isp": "中国电信",
    "latitude": "34.106632",
    "longitude": "108.791722",
    "provinceCode": "610000",
    "provinceName": "陕西省",
    "timeZone": "UTC+08:00",
    "zipcode": "710000"
    },
    "exec_time": 0.085515,
    "ip": "你的访问ip",
    "msg": "操作成功"
}
```

**Contact:**

If you have any questions about this plugin, please contact the author or create an issue: [guhx](https://github.com/billy723/dify-plugin-jishishuke/issues). For questions about JishiShuke itself, please refer to https://api.jishishuke.com