# Company Reviews Web Application

Service File: `/etc/systemd/system/company_reviews.service` 

Commands to start the service:

```bash
sudo systemctl start   company_reviews
sudo systemctl enable  company_reviews
sudo systemctl restart company_reviews
```

Server block configuration file: `/etc/nginx/sites-available/company_reviews` , symlink in `/etc/nginx/sites-enabled`

To verify syntax of the server configs: 
```bash
sudo nginx -t
```

Restart the server: 

```bash
sudo systemctl restart nginx
```

Tell firewall to let traffic in and out ofthe web server: 
```bash
sudo ufw allow 'Nginx Full'
```
