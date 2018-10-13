#include "distributedLock.h"
#include <iostream>
#include <Rpcdce.h>

/* Generate ClientId and establish a connection to a Server*/
DistributedLock::DistributedLock(std::string serverAddr)
{
	clientId = getClientID()
}

std::string getClientID()
{
	char buf[50];
    memset(buf, 0, sizeof(buf));
    GUID guid;
    if (S_OK == ::CoCreateGuid(&guid)) {
        sprintf_s(buf, 50, "{%08X-%04X-%04x-%02X%02X-%02X%02X%02X%02X%02X%02X}"
            , guid.Data1
            , guid.Data2
            , guid.Data3
            , guid.Data4[0], guid.Data4[1]
            , guid.Data4[2], guid.Data4[3], guid.Data4[4], guid.Data4[5]
            , guid.Data4[6], guid.Data4[7]);
    }
    return std::string(buf);
}