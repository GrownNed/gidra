#include "Python.h"

typedef void (*capsule_dest)(PyObject *);
typedef void (*cobj_dest)(void *);

#if PY_MAJOR_VERSION == 2 && PY_MINOR_VERSION <= 6
	#define CAP_NEW(a,b,c) PyCObject_FromVoidPtr(a,c)
	#define DEST_FUNC_TYPE cobj_dest
	#define CAP_GET_POINTER(a,b) PyCObject_AsVoidPtr(a)
#else
	#define CAP_NEW PyCapsule_New
	#define DEST_FUNC_TYPE capsule_dest
	#define CAP_GET_POINTER PyCapsule_GetPointer
#endif

PyObject* make_capsule(void *p, const char *name, capsule_dest dest) {
    return CAP_NEW(p, name, (DEST_FUNC_TYPE)dest);
}
void* get_pointer(PyObject *cap, const char *name) {
    return CAP_GET_POINTER(cap, name);
}
