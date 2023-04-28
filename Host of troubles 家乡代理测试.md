[toc]

# Host of troubles 家乡代理测试

## 测试流程

### 确认存在缓存

+ 以 absolute-URI 为 http://hostT，唯一 host 头为 host: hostT 的请求连续请求 hostT，每次请求携带请求编号。
+ 若后续请求未引发服务器输出，获得的编号为之前的请求所携带的编号，则存在缓存，对其行为进行测试。

### Presence of host

+ Absent：发送既无 host 头也无绝对 URI 的请求。
  + 若收到响应为 400，则记录为 Reject。
  + 若收到响应为 200，则记录为 Allow。

+ Host header：发送无 host 头，有绝对 URI 的请求。
  + 若收到响应为 400，则记录为 Must。
  + 若收到响应为 200，则记录为 Optional。

+ Absolute-URI：发送有 host 头，无绝对 URI 的请求。
  + 若收到响应为 400，则记录为 Must。
  + 若收到响应为 200，则记录为 Optional。

### Recognized absolute-URI vs. Recognized Host header

+ Consistency：发送 absolute-URI 为 http://hostA，唯一 host 头为 host: hostB 的请求。
  + 若收到响应为 400，则记录为 Must。
  + 若收到响应为 200，则记录为 Optional，并额外进行 Preference 的记录。
+ Preference：根据服务器响应进行记录。
  + 若服务器收到的请求为 hostA，则记录为 Absolute-URI。
  + 若服务器收到的请求为 hostB，则记录为 Host header。

### Multiple Host headers

+ 若 Consistency 为 Must，则发送 absolute-URI 为 http://hostA，host 头为 host: hostA 和 host: hostB 的请求。

  + 若收到响应为 200，则记录为 Prefer first。
  + 若收到响应为 400，则发送 absolute-URI 为 http://hostB，host 头为 host: hostA 和 host: hostB 的请求。
    + 若收到响应为 200，则记录为 Prefer last。
    + 若收到响应为 400，则发送 absolute-URI 为 http://hostA, hostB，host 头为 host: hostA 和 host: hostB 的请求。
      + 若收到响应为 200，则记录为 Concenate。
      + 若收到响应为 400，则记录为 Reject。
+ 若 presence of Absolute-URI 为 Must，且 Preference 为 Absolute-URI，则跳过。
+ 若 presence of Absolute-URI 为 Must，且 Preference 为 Host header，则发送 absolute-URI 为 http://hostC，带有 host: hostA 和 host: hostB 的多 host 头请求。

  + 若收到响应为 400，则记录为 Reject。
  + 若收到响应为 200，则根据服务器响应进行记录：
    + 若服务器收到的请求为 hostA，则记录为 Prefer first。
    + 若服务器收到的请求为 hostB，则记录为 Prefer last。
    + 若服务器收到的请求为 hostC，则记录为 Use absolute-URI。
    + 若服务器收到的请求为 hostA, hostB，则记录为 Concatenate。

### Space-preceded Host as first header

+ 若 Consistency 为 Must，则发送 absolute-URI 为 http://hostA，第一个头为 host: hostA（前带空格），无其他 host 头的请求。
  + 若收到响应为 200，则记录为 Recognize。
  + 若收到响应为 400，则发送 absolute-URI 为 http://hostB，第一个为 host: hostA（前带空格），第二个 host: hostB 的请求。
    + 若收到响应为 200，则记录为 Not recognize。
    + 若收到响应为 400，则记录为 Reject。
+ 若 presence of Absolute-URI 为 Must，且 Preference 为 Absolute-URI，则跳过。
+ 若 presence of Absolute-URI 为 Must，且 Preference 为 Host header 则提供 HTTP 形式 absolute-URI；若 presence of Absolute-URI 为 Optional，则仅在需要时提供，之后请求方式如下：
  + 若 presence of Host header 为 Must，则发送第一个头为 host: hostA（前带空格），无其他 host 头的请求。
    + 若收到响应为 200，则记录为 Recognize。
    + 若收到响应为 400，则发送第一个头为 host: hostA （前带空格），有另一个正常 host 头 host: hostB 的请求。
      + 若收到响应为 400，则记录为 Reject。
      + 若收到响应为 200，则记录为 Not recognize。
  + 若 presence of Host header 为 Optional，则发送一个 absolute-URI 为 hostB，第一个头为 host: hostA （前带空格），无其他 host 头的请求。
    + 若收到响应为 400，则记录为 Reject。
    + 若收到响应为 200，则根据服务器响应进行记录：
      + 若服务器收到的请求为 hostA，则记录为 Recognize。
      + 若服务器收到的请求为 hostB，则记录为 Not recognize。

### Other space-preceded Host header

+ 若 Consistency 为 Must，则发送 absolute-URI 为 http://hostA，第二个头为 host: hostA（前带空格），无其他 host 头的请求。
  + 若收到响应为 200，则记录为 Recognize。
  + 若收到响应为 400，则发送 absolute-URI 为 http://hostB，第一个头为 hostB，第二个头为 host: hostA（前带空格），无其他 host 头的请求。
    + 若收到响应为 200，则记录为 Not recognize。
    + 若收到响应为 400，则发送 absolute-URI 为 http://hostBhost: hostA，第一个头为 hostB，第二个头为 host: hostA（前带空格），无其他 host 头的请求。
      + 若收到响应为 200，则记录为 Line folding。
      + 若收到响应为 400，则记录为 Reject。
+ 若 presence of Absolute-URI 为 Must，且 Preference 为 Absolute-URI，则跳过。
+ 若 presence of Absolute-URI 为 Must，且 Preference 为 Host header 则提供 HTTP 形式 absolute-URI；若 presence of Absolute-URI 为 Optional，则仅在需要时提供，之后请求方式如下：
  + 若 presence of Host header 为 Must，则发送第二个头为 host: hostA（前带空格），无其他 host 头的请求。
    + 若收到响应为 200，则记录为 Recognize。
    + 若收到响应为 400，则发送第一个头为 host: hostA，第二个头为 host: hostB（前带空格），无其他 host 头的请求。
      + 若收到响应为 400，则记录为 Reject。
      + 若收到响应为 200，则根据服务器响应进行记录：
        + 若服务器收到的请求为 hostA，则记录为 Not recognize。
        + 若服务器收到的请求为 hostAhost: hostB，则记录为 Line folding。
  + 若 presence of Host header 为 Optional，则发送发送一个 absolute-URI 为 hostB，第二个头为 host: hostA （前带空格），无其他 host 头的请求。
    + 若收到响应为 400，则记录为 Reject。
    + 若收到响应为 200，则根据服务器响应进行记录：
      + 若服务器收到的请求为 hostA，则记录为 Recognize。
      + 若服务器收到的请求为 hostB，则需要继续测试：发送一个有无关的 absolute-URI，第二个头为 host: hostA，第三个头为 host: hostB（前带空格），无其他 host 头的请求。根据服务器响应进行记录：
        + 若服务器收到的请求为 hostA，则记录为 Not recognize。
        + 若服务器收到的请求为 hostAhost: hostB，则记录为 Line folding。

### Space-succeeded Host header

与 Space-preceded Host as first header 一致。

### schema of absolute-URI

+ 若 Consistency 为 Must，则发送 absolute-URI 为 nonhttp://hostA，host 头为 host: hostA 的请求。
  + 若收到响应为 200，则发送 absolute-URI 为 nonhttp://hostB，host 头为 host: hostA 的请求。
    + 若收到响应为 400，则记录为 Recognize any。
    + 若收到响应为 200，则发送 absolute-URI 为 https://hostB，host 头为 host: hostA 的请求。
      + 若收到响应为 400，则记录为 Recognize HTTP/S, not others。
      + 若收到响应为 200，则发送 absolute-URI 为 http://hostB，host 头为 host: hostA 的请求。
        + 若收到响应为 400，则记录为 Recognize HTTP, not others。
  + 若收到响应为 400，则进行进一步判断：
    + presence of Absolute-URI 为 Optional，则发送 absolute-URI 为 https://hostA，host 头为 host: hostA 的请求。
      + 若收到响应为 200，则记录为 Recognize HTTP/S, reject others。
      + 若收到响应为 400，则记录为 Recognize HTTP, reject others。
    + presence of Absolute-URI 为 Must，则发送 absolute-URI 为 https://hostA，host 头为 host: hostA 的请求。
      + 若收到响应为 200，则记录为 Recognize HTTP/S。
      + 若收到响应为 400，则记录为 Recognize HTTP。
+ 若 presence of Host header 为 Must，且 Preference 为 Host header，则跳过。
+ 若 presence of Host header 为 Must，且 Preference 为 Absolute-URI，则请求方式如下：
  + 发送绝对 URI 为 https://hostA，host 头为 host: hostB 的请求。
    + 若收到响应为 400，则记录为 Recognize HTTP, reject others。
    + 若收到响应为 200，则根据服务器响应进行记录：
      + 若服务器收到的请求为 hostB，则记录为 Recognize HTTP, not others。
      + 若服务器收到的请求为 hostA，则继续测试：发送绝对 URI 为 nonhttp://hostA，host 头为 host: hostB 的请求。
        + 若收到响应为 400，则记录为 Recognize HTTP/S, reject others。
        + 若收到响应为 200，则根据服务器响应进行记录：
          + 若服务器收到的请求为 hostB，则记录为 Recognize HTTP/S, not others。
          + 若服务器收到的请求为 hostA，则记录为 Recognize any。
+ 若 presence of Host header 为 Optional，则请求方式如下：
  + 发送绝对 URI 为 HTTPS ，无 host 头的请求。
    + 若收到响应为 400，则继续测试，为原请求增加 host 头。
      + 若收到响应为 200，则记录为 Recognize HTTP, not others。
      + 若收到响应为 400，则记录为 Recognize HTTP, reject others。

    + 若收到响应为 200，则继续测试，发送绝对 URI 为 nonHTTP，无 host 头。
      + 若收到响应为 200，则记录为 Recognize any。

      + 若收到响应为 400，则继续测试，为原请求增加 host 头。
        + 若收到响应为 200，则记录为 Recognize HTTP/S, not others。
        + 若收到响应为 400，则记录为 Recognize HTTP/S, reject others。

