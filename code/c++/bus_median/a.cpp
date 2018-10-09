#include <iostream>
#include <vector>
#include <map>
#include <functional>
#include <fstream>
#include <sstream>
#include <string>
#include <set>
#include <sstream>
using namespace std;

int main()
{
    string predpath = "../bus_data/train1-24/train20171012.csv";
    set<string> res;
    ifstream fin(predpath.c_str()); //c_str()返回char型指针
    string str, substri;
    string printfpath = "../bus_data/train1-24/test_train20171012.csv";
    ofstream fou(printfpath.c_str());
    getline(fin, str); //按行读入文件，传入str
    fou << str << endl;
    for (int i = 0; i < 26397678; i++)
    {
        getline(fin, str);
        res.insert(str); //res保存busid-hour-up
    }
    fin.close();

    for (set<string>::iterator it = res.begin(); it != res.end(); ++it)
        fou << *it << endl;
    fou.close();
    return 0;

    /*string predpath = "../bus_data/train1-24/train20171008.csv";
    vector<string> res;
    ifstream fin(predpath.c_str()); //c_str()返回char型指针
    string str, substri;
    //getline(fin, str); //按行读入文件，传入str
    for (int i = 0; i < 10000; i++)
    {
        getline(fin, str);
        res.push_back(str); //res保存busid-hour-up
    }
    fin.close();

    string printfpath = "../bus_data/train1-24/train20171040.csv";
    ofstream fou(printfpath.c_str());
    for (vector<string>::iterator it = res.begin(); it != res.end(); ++it)
        fou << *it << endl;
    fou.close();
    return 0;*/
}