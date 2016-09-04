include "common.thrift"
const i32 WMESSAGE_V1_GET = 1025

enum GetStatus
{
    Success,
    NoSuchUser,
    PasswordWrong,
    TooManyTimes,
    NoData,
    Exception,
    NotSupported
}

struct GetRequest
{
    1:common.ResType Type;
    2:string UserName;
    3:string Password;
    4:string TradingDay;
}

struct GetResponse
{
    1:common.ResType Type;
    2:GetStatus Status;
    3:string Content;
    4:string Key;
}
