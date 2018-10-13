// windows socket
#include <stdio.h>
#include <Winsock2.h>
#include "connectionBase.h"
#include <map>

using namespace std;

/**
definition of functions for follower server
**/
class Follower{
public:
	Follower(std::string serverAddr);
	~Follower();
	void updateMap();
private:
	map<std::string, std::string> lockMap;
	bool isConnected; // connection status with leader server
}