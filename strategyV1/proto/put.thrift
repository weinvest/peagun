include "common.thrift"

const i32 WMESSAGE_V1_PUT = 1026
enum PutStatus
{
    Success,
    Exists,
    Exception
}

struct PutRequest
{
    1:common.ResType Type;
    2:string TradingDay;
    3:string Content;
}

struct PutResponse
{
    1:common.ResType Type;
    2:PutStatus Status;
    3:string UserName;
    4:string Password;
}

const i32 WMESSAGE_V1_UPDATE = 1027
enum UpdateStatus
{
    Success,
    NotExists,
    Exception
}

struct UpdateRequest
{
    1:common.ResType Type;
    2:string TradingDay;
    3:string Content;
}

struct UpdateResponse
{
    1:common.ResType Type;
    2:UpdateStatus Status;
}

const i32 WMESSAGE_V1_AUTH = 1028
enum AuthStatus
{
    Success,
    NotExists,
    Exception
}

struct AuthRequest
{
    1:string TradingDay;
}

struct AuthResponse
{
    1:AuthStatus Status;
    2:string UserName;
    3:string Password;
}