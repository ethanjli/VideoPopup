all:
	swig -python myfilter.i

	g++ -O3 -ffast-math -shared -fPIC myfilter.cpp myfilter_wrap.c -w -o _myfilter.so \
	  -I/usr/local/lib/python2.7/dist-packages/numpy/core/include \
	  -I/usr/include/python2.7/
