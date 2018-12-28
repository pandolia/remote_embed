import sys, socket, threading, traceback, os, inspect, subprocess

PY3 = sys.version_info[0] == 3

class Disconnect(Exception):
    pass

class Object():
    def __init__(self, **kw):
        for k, v in kw.items():
            self.__dict__[k] = v

def nullfunc(*args, **kwargs):
    pass

class Log:
    def __init__(self, writer, name='Remote-Embed'):
        if not hasattr(writer, 'write'):
            self.info = nullfunc
            self.error = nullfunc
            return
        flush = getattr(writer, 'flush', nullfunc)
        self.name = name
        self.write = lambda s: (writer.write(s), flush())

    def info(self, s):
        try:
            self.write('(%s) %s\n' % (self.name, s))
        except IOError:
            pass

    def error(self, s):
        try:
            self.write('(%s) %s\n%s' % (self.name, s, traceback.format_exc()))
        except IOError:
            pass


# verbose = Log(sys.stderr, 'VERBOSE').info

def Embed(
    host='127.0.0.1',
    port=0,
    popup=None,
    log_writer=sys.stderr,
    this_coding=None,
    debugger_coding=None,
    help_info=None
):
    if this_coding is None:
        this_coding = 'gb18030' if os.name == 'nt' else 'utf8'
    
    if debugger_coding is None:
        debugger_coding = this_coding

    def embed():
        log = Log(log_writer)
        
        lineinfo = inspect.stack()[1]
        log.info('Break at: %s, line %d, %s' % lineinfo[1:4])
        log.info('--------> %s' % lineinfo[4][0].strip())

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, port))
            _port = sock.getsockname()[1]
            sock.listen(1)
        except:
            log.error('Failed to listen on %s:%d!' % (host, port))
            log.info('Resume the execution.')
            sock.close()
            return

        log.info('Listen at %s:%d, waiting for the remote debugger to attach...' % (host, _port))    
        _popup(popup, host, _port)

        try:
            conn, addr = sock.accept()
        except:
            log.error('Failed to accept a connection!')
            log.info('Resume the execution.')
            sock.close()
            return
        
        log.info('Be attached by the remote debugger at %s:%d.' % addr)

        _help_info = help_info or '\n'.join([
            'Attached to the remote process at %s:%d.' % (host, _port),
            'Remote Python version: %s' % sys.version,
            'Remote cwd: %s' % os.getcwd(),
            'Remote breakpoint: %s, line: %d, %s' % lineinfo[1:4],
            '-----------------> %s' % lineinfo[4][0].strip(),
        ])
        
        def send(s):
            if not PY3:
                if type(s) is unicode:
                    s = s.encode(debugger_coding)
                else:
                    if type(s) is not str:
                        s = str(s)
                    if this_coding != debugger_coding:
                        s = s.decode(this_coding).encode(debugger_coding)
            else:
                if type(s) is str:
                    s = s.encode(debugger_coding)
                elif type(s) is bytes:
                    if this_coding != debugger_coding:
                        s = s.decode(this_coding).encode(debugger_coding)
                else:
                    s = str(s).encode(debugger_coding)
            try:
                conn.sendall(s)
            except socket.error:
                raise Disconnect
        
        def recv():
            try:
                code = conn.recv(1024)
            except socket.error:
                code = ''
            if not code:
                raise Disconnect
            if this_coding != debugger_coding:
                code = code.decode(debugger_coding).encode(this_coding)
            return code.strip()

        try:
            send(_help_info + '\n>>> ')
        except:
            log.error('Failed to send help infomation to the remote debugger!')
            log.info('Resume the execution.')
            conn.close()
            sock.close()
            return

        fileobj = Object(write=send, flush=nullfunc)
        oldout, olderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = fileobj, fileobj
        _locals = inspect.currentframe().f_back.f_locals
        _globals = inspect.currentframe().f_back.f_globals

        try:
            while True:
                code = recv()
                if code in (b'exit', b'quit', b'exit()', b'quit()'):
                    log.info('The remote debugger exit.')
                    break
                _coding = this_coding.encode(this_coding) if PY3 else this_coding
                code = b'#coding=%s\n%s' % (_coding, code)
                try:
                    try:
                        bytecode = compile(code, '<stdin>', 'eval')
                    except SyntaxError:
                        exec(code, _globals, _locals)
                        send('>>> ')
                    else:
                        send(eval(bytecode, _globals, _locals))
                        send('\n>>> ')
                except SystemExit:
                    log.info('The remote debugger exit.')
                    break
                except BaseException:
                    send(traceback.format_exc())
                    send('>>> ')
        except Disconnect:
            log.info('The remote debugger disconnected.')
        except BaseException:
            log.error('Embarassing...')
        finally:
            log.info('Resume the execution.')
            sys.stdout, sys.stderr = oldout, olderr
            conn.close()
            sock.close()
    
    return embed

def _popup(popup, host, port):
    if not popup:
        return

    if isinstance(popup, str):
        if os.name == 'nt':
            subprocess.call(['start', popup, host, str(port)], shell=True)
            return
        
        # TODO: add MacOS, Linux support

        return

    if callable(popup):
        popup(host, port)

if __name__ == '__main__':
    # runs in windows('gb18030'), attaches from linux('utf8')
    # embed = Embed('0.0.0.0', 9999, this_coding='gb18030', debugger_coding='utf8')

    embed = Embed(popup='./test/nc.exe')

    a = 2

    def func(x, y, z):
        print(a, x, y, z); sys.stdout.flush()
        embed()
        print(a, x, y, z); sys.stdout.flush()

    func(1, 2, [3])
