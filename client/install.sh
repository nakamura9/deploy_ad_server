apt-get update
apt-get install python-requests
apt-get install python-twisted
apt-get install python-psutil

apt-get install vlc
apt-get install git

git clone https://github.com/nakamura9/deploy_ad_server.git
cd deploy_ad_server/client
echo "First open vlc and configure the unix socket. Then register the client id with the ad server. Finally run the application using the command python http_client.py <id> <host_of_server> <port>"