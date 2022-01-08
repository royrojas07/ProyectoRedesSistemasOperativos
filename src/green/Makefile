APPNAME = server
CXX = g++
CPPFLAGS = -g -Wall -Wextra
LIBS = -lm -pthread


SOURCE =  $(wildcard green/*.cpp agent/*.cpp link_layer/*.cpp \
 network_layer/*.cpp transport_layer/*.cpp log/*.cpp\
  struct/*.cpp packet/*/*.cpp stats/*.cpp)
OBJECTS=$(SOURCE:.cpp=.o)
HEADERS = $(wildcard agent/*.h link_layer/*.h \
 network_layer/*.h transport_layer/*.h struct/*.h packet/*/*.h stats/*.h)  
HEADERS2 = $(HEADERS:.h=.h.gch)

programa: $(OBJECTS)
	$(CXX) -o $(APPNAME) $^ $(CFLAGS) $(LIBS)

%.o: %.cpp %.h
	$(CXX) -c $< -o $@ $(CXXFLAGS) -g

print-%  : ; @echo $* = $($*)

.PHONY: clean
clean:
	rm -rf $(APPNAME) $(OBJECTS) $(HEADERS2)
