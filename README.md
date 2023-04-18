# Host_of_Troubls_Server

+ 本地使用方法: python Server.py <-m M> <-f F> <-o O> <-s S> <-a A> <-p P>
+ 参数解释：
  + -m: 多 Host 头处理原则
    + M = 0: Reject
    + M = 1: Prefer first （默认值）
    + M = 2: Prefer last
  + -f: 第一个头前有空格的处理原则
    + F = 0: Not recognize
    + F = 1: Recognize （默认值）
    + F = 2: Reject
  + -o: 后续头有前有空格的处理原则
    + O = 0: Line folding （默认值）
    + O = 1: Not recognize
  + -s: 头后有空格的处理原则
    + S = 0: Not recognize
    + S = 1: Recognize （默认值）
  + -a: 绝对 URL 的处理原则
    + R = 0: Recognize HTTP, not others （默认值）
    + R = 1: Recognize HTTP/S, reject others
    + R = 2: Recognize HTTP/S, not others
    + R = 3: Recognize any schema
  + -p: 同时有 host 头和 URL 的选择
    + P = 0: Absolute-URL （默认值）
    + P = 1: Host header
