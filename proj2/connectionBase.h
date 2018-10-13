// windows socket
#include <stdio.h>
#include <Winsock2.h>
using namespace std;

/*
base class for constructing a connection by using socket
send msg + listen msg 
UDP by default
*/
class ConnectionBase
{
public:
	ConnectionBase(std::string serverAddr);
	~ConnectionBase();
	void send_msg(std::string msg);
	// listen on specific ports or other ways to listen messages?
	void listen_msg();
	std::string getServerAddr();
	int getVersion();
private:
	std::string serverAddr;
	int version; // current version
}