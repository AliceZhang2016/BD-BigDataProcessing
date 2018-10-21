// windows socket
#include <stdio.h>
#include <Winsock2.h>
#include "connectionBase.h"
#include <map>

using namespace std;

/**
definition of functions for follower server
**/
class Leader: public ConnectionBase
{
public:
	Leader(std::string followerAddr[], int follower_num);
	~Leader();
	void updateMap();
	void sendUpdateCommand(); // maybe use broadcast
private:
	map<std::string, std::string> lockMap;
	bool isConnected; // connection status with leader server
	// could use an array to store the ip address of 
	// all the follower servers which have a connection
	// with this leader server
	std::string followersAddr[100]; 
	int follower_num;
}