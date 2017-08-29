# Company Reviews Web Application

Service File: `/etc/systemd/system/company_reviews.service` 

Commands to start the service
`
sudo systemctl start myproject
sudo systemctl enable myproject
sudo systemctl restart myproject
`

Server block configuration file: `/etc/nginx/sites-available/company_reviews` symlink in `/etc/nginx/sites-enabled`

To verify syntax of the server configs: `sudo nginx -t`

Restart the server: `sudo systemctl restart nginx`
Tell firewall to let traffic in and out ofthe web server: `sudo ufw allow 'Nginx Full'`
