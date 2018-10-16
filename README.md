# BD-BigDataProcessing
projects of BD in master 2-1
semester project could be seen on the website:
http://www.cs.sjtu.edu.cn/~wuct/bdpt2/project.html

## project 2 - Distributed Lock Design 分布式锁
根据project需求，系统中共有三种不同的角色：leader server, follower server, client，因此需要实现3个class
整个系统围绕client的功能展开，共有三：
* Preempting a distributed lock 请求锁
* Releasing a distributed lock 释放锁
* Checking a distributed lock 查看锁是否归属于自己

需要注意的几个问题：
* client只与follower server通信
* leader server只与follower server通信
* 死锁的出现和解决，超时释放等的设置
* 动作的顺序
---
#### 请求锁
1. client: 查看锁的归属 - 如果锁不属于自己，再进行以下的操作
2. client -> follewer server: send request
3. client: wait the response (超时设置)
    * 如果等到response一切都好
    * 没等到就下次再请求了(请求之前可查看锁的归属，如果已经属于自己，就不用请求了)
4. follower server: listen the port to get msg from client
5. follower server: forward the msg to leader server
6. follower server: wait response from leader server (超时设置)     
    * 如果 ***1.等到server update的信号，就表明拿到了response 2.等到response表明不能获取当前锁。***  那么表明connection没有问题，然后follower server即可将相应的response回复给处于等待状态的client(丢包情况同样可能发生，client可以在超时之后重新请求)
    * 如果超时的时候依旧没有获取到来自leader server的任何有效信息，那么过一段时间重新进行第5步。connection出错超过一定次数，就直接不回应给client(**?需要斟酌**)
7. leader server: listen msg from all follower servers
8. leader server: send **update command** to follower servers to update their maps.
    * ***如果服务器在发完update command之后突然down掉***，follower server将不会获取到response，但follower server已经达到了第6步中的第一种情况，于是一切可以继续顺利运行
    * ***如果某个follower server没有成功收到update command(比如丢包)*** , 于是该follower server维护的map还是旧的话。可以采取：每隔一段时间follower server与leader server确认一波版本号的方法。
9. leader server: send **response** to follower server who send the preemting request
10. follower server: 执行第6步中的小节1，即返回response给client

---
#### 释放锁
1. client: 查看锁的归属 - 如果锁属于自身，则进行下面的操作
2. 剩下的操作同请求锁

---
#### 查看锁的归属
1. client -> follower server: send msg to check the status of lock
    * 有超时设置，如果超时，则一段时间后重新请求
2. follower server: 查询自己的map，并将response返回给client
