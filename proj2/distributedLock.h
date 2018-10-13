#ifndef DISTRIBUTEDLOCK_H
#define DISTRIBUTEDLOCK_H
#include <string>

using namespace std;

class DistributedLock : public ConnectionBase
{
public:
    /* Generate ClientId and establish a connection to a Server*/
    DistributedLock(std::string serverAddr);
    ~ DistributedLock();
    bool TryLock(std::string lockKey);
    bool TryUnlock(str::string lockKey);
    bool OwnTheLock(std::string lockKey);
private:
    /*Generate ClientId based on UUID*/
    std::string GetClientId();
    /*Attempt to connect to a Server*/
    bool ConnectToFollower(std::string serverAddr);
    std::string clientId;
    bool isConnected;
    int fd; // the descriptor used to talk to the consensus system
}

#endif // DISTRIBUTEDLOCK_H