# Facebook_Crawler
The project is developed by Teng-Lin Yu(游騰林). If you have any questions or suggestions, please feel free to contact me. 

## Support

[![ecgo.png](https://raw.githubusercontent.com/TLYu0419/facebook_crawler/main/images/ecgo.png)](https://payment.ecpay.com.tw/QuickCollect/PayData?GcM4iJGUeCvhY%2fdFqqQ%2bFAyf3uA10KRo%2fqzP4DWtVcw%3d)


**Donate is not required to utilize this package**, but web crawler projects need much time to maintain and developed. If you could support me, I will really appreciate it. Either donate, star or share is good for me. Your support will help me to maintain and develop more functions.

**捐款不是使用這個套件的必要條件**，但網路爬蟲專案都會需要花費相當多時間來維護和開發，如果你能支持我我會非常感謝。不論是捐款、給星星或跟朋友分享對我來說都是非常好的支持方式。你的支持會是我維護和繼續開發新功能的動力

## What's this?

The project could help us collect data from Facebook's public Fanspage / group. Here are the three big points of this project: 
1. You don't need to log in to your account.
2. Easy to use: Just key in the Fanspage/group URL and the target date. 
3. Efficiently: It collects the data through request directly instead of Selenium.


這個專案可以幫我們從 Facebook 公開的的粉絲頁和公開社團收集資料。以下是本專案的 3 個重點:
1. 不需登入: 不需要帳號密碼因此也不用擔心被鎖定帳號
2. 簡單: 僅需要粉絲頁/社團的網址和停止的日期(用來跳脫迴圈)
3. 高效: 透過 request 直接向伺服器請求資料，不需通過 Selenium

## Quickstart
- Install Method
  ```pip
  pip install facebook-crawler
  ```

- Facebook Fanspage 
  ```python
  import facebook_crawler
  pageurl= 'https://www.facebook.com/diudiu333'
  facebook_crawler.Crawl_PagePosts(pageurl=pageurl, until_date='2021-01-01')
  ```
  ![quickstart_fanspage.png](https://raw.githubusercontent.com/TLYu0419/facebook_crawler/main/images/quickstart_fanspage.png)
- Group
  ```python
  import facebook_crawler
  groupurl = 'https://www.facebook.com/groups/pythontw'
  facebook_crawler.Crawl_GroupPosts(groupurl, until_date='2021-01-01')
  ```
  ![quickstart_group.png](https://raw.githubusercontent.com/TLYu0419/facebook_crawler/main/images/quickstart_group.png)
## License
- [Apache License 2.0](https://github.com/TLYu0419/facebook_crawler/blob/main/LICENSE)
- 本專案提供的所有內容均用於教育、非商業用途。本專案不對資料內容錯誤、更新延誤或傳輸中斷負任何責任。

## Contact
- Email: tlyu0419@gmail.com
- Facebook: https://www.facebook.com/tlyu0419
- Any suggestions is good and feel free to contact me.


## To Do
- GUI interface
- Database

