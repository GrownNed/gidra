from cpython.pycapsule cimport *
from libc.stdint cimport uint32_t, int32_t
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cpython.object cimport PyObject

cdef extern from "ikcp.h":
    ctypedef uint32_t ISTDUINT32; #for linux
    ctypedef int32_t ISTDINT32; #for linux
    ctypedef ISTDINT32 IINT32;
    ctypedef ISTDUINT32 IUINT32;

    struct IQUEUEHEAD:
        IQUEUEHEAD *next, *prev

    struct IKCPCB:
        IUINT32 conv, token, mtu, mss, state;
        IUINT32 snd_una, snd_nxt, rcv_nxt;
        IUINT32 ts_recent, ts_lastack, ssthresh;
        IINT32 rx_rttval, rx_srtt, rx_rto, rx_minrto;
        IUINT32 snd_wnd, rcv_wnd, rmt_wnd, cwnd, probe;
        IUINT32 current, interval, ts_flush, xmit;
        IUINT32 nrcv_buf, nsnd_buf;
        IUINT32 nrcv_que, nsnd_que;
        IUINT32 nodelay, updated;
        IUINT32 ts_probe, probe_wait;
        IUINT32 dead_link, incr;
        IQUEUEHEAD snd_queue;
        IQUEUEHEAD rcv_queue;
        IQUEUEHEAD snd_buf;
        IQUEUEHEAD rcv_buf;
        IUINT32 *acklist;
        IUINT32 ackcount;
        IUINT32 ackblock;
        void *user;
        char *buffer;
        int fastresend;
        int nocwnd;
        int logmask;
        int (*output)(const char *buf, int len, IKCPCB *kcp, void *user);
        void (*writelog)(const char *log, IKCPCB *kcp, void *user);
    
    ctypedef IKCPCB ikcpcb;
    ikcpcb* ikcp_create(IUINT32 conv, IUINT32 token, void *user);
    void ikcp_release(ikcpcb *kcp);
    int ikcp_recv(ikcpcb *kcp, char *buffer, int len);
    int ikcp_send(ikcpcb *kcp, const char *buffer, int len);
    void ikcp_update(ikcpcb *kcp, IUINT32 current);
    IUINT32 ikcp_check(const ikcpcb *kcp, IUINT32 current);
    int ikcp_input(ikcpcb *kcp, const char *data, long size);
    void ikcp_flush(ikcpcb *kcp);
    int ikcp_wndsize(ikcpcb *kcp, int sndwnd, int rcvwnd);
    int ikcp_nodelay(ikcpcb *kcp, int nodelay, int interval, int resend, int nc);
    int ikcp_setmtu(ikcpcb *kcp, int mtu);

cdef extern from "compat.h":
    ctypedef void (*capsule_dest)(PyObject *)
    object make_capsule(void *, const char *, capsule_dest)
    void* get_pointer(object, const char*)

cdef struct UsrInfo:
    int handle

g_KcpAgentCbs = {}

RECV_BUFFER_LEN = 4*1024*1024

cdef char* recv_buffer = <char *>PyMem_Malloc(sizeof(char)*RECV_BUFFER_LEN)

cdef int kcp_output_callback(const char *buf, int len, ikcpcb *kcp, void *arg):
    global g_KcpAgentCbs
    cdef UsrInfo *c = <UsrInfo *>arg;
    uid = <object>c.handle
    cb = g_KcpAgentCbs[uid]
    cb(uid, buf[:len])
    return 0

cdef void del_kcp(PyObject *obj):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>obj, NULL)
    cdef UsrInfo *c = NULL
    if ckcp.user != NULL:
        global g_KcpAgentCbs
        c = <UsrInfo *>ckcp.user
        uid = <object>c.handle
        del g_KcpAgentCbs[uid]
        PyMem_Free(c)
        c = NULL
        ckcp.user = NULL
    ikcp_release(ckcp)

def lkcp_create(conv, token, uid, cb):
    global g_KcpAgentCbs
    g_KcpAgentCbs[uid] = cb
    cdef UsrInfo *c = <UsrInfo *>PyMem_Malloc(sizeof(UsrInfo))
    c.handle = <int>uid
    cdef ikcpcb* ckcp = ikcp_create(conv, token, c)
    ckcp.output = kcp_output_callback
    return make_capsule(ckcp, NULL, del_kcp)

def lkcp_recv(kcp):
    global recv_buffer
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    hr = ikcp_recv(ckcp, recv_buffer, RECV_BUFFER_LEN)
    if hr <= 0:
        return hr,None
    else:
        return hr,recv_buffer[:hr]

def lkcp_send(kcp, data):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    cdef char* ptr = data
    cdef size_t size = len(data)
    return ikcp_send(ckcp, ptr, size)

def lkcp_update(kcp, current):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    cdef int32_t i_cur = current
    ikcp_update(ckcp, i_cur)

def lkcp_check(kcp, current):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    cdef int32_t i_cur = current
    return ikcp_check(ckcp, i_cur)

def lkcp_input(kcp, data):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    cdef char* ptr = data
    cdef size_t size = len(data)
    return ikcp_input(ckcp, ptr, size)

def lkcp_flush(kcp):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    ikcp_flush(ckcp)

def lkcp_wndsize(kcp, sndwnd, rcvwnd):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    cdef int32_t i_nsnd = sndwnd
    cdef int32_t i_nrcv = rcvwnd
    ikcp_wndsize(ckcp, i_nsnd, i_nrcv)

def lkcp_nodelay(kcp, nodelay, interval, resend, nc):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    cdef int32_t i_nodelay = nodelay
    cdef int32_t i_interval = interval
    cdef int32_t i_resend = resend
    cdef int32_t i_nc = nc
    return ikcp_nodelay(ckcp, i_nodelay, i_interval, i_resend, i_nc)

def lkcp_setmtu(kcp, mtu):
    cdef ikcpcb* ckcp = <ikcpcb*>get_pointer(<object>kcp, NULL)
    ikcp_setmtu(ckcp, mtu)