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

// 分割字符串的函数……
vector<string> SplitLine(string stringplit, string strs)
{
	vector<string> res;
	//string::size_type pos;
	int pos(-1);
	strs += stringplit;
	int size = int(strs.size());

	for (int i = 0; i < size; i++)
	{
		pos = strs.find(stringplit, i);
		if (pos < size)
		{
			string tempstr = strs.substr(i, pos - i);
			res.push_back(tempstr);
			i = pos + int(stringplit.size()) - 1;
		}
	}
	return res;
}

// 读测试集，然后把待预测线路搞出来，目的是为了从训练集中找数据
// set<string>的string内容为  busid-predTime-up。
set<string> loadTargetBusTimeUP(string datapath);

// 然后，根据待预测的线路，把所有的这些训练集中对应的数据都找出来
map<string, double> loadTrainBusTimeUPStop(string basicpath, set<string> targetBusTimeUp);

// 再次读测试集！给出预测的时间！
map<string, vector<double>> predPathTimes(string basicpath, map<string, double> busTimeUpStopCost, string respath);

int main()
{
	string predPath = "C:/Users/Administrator/Desktop/toBePredicted_update_0523.csv";
	set<string> targetBusTimeUp = loadTargetBusTimeUP(predPath);

	string basicpath = "C:/Users/Administrator/Desktop/train1-24/train2017";
	map<string, double> busTimeUpStopCost = loadTrainBusTimeUPStop(basicpath, targetBusTimeUp);

	string respath = "C:/Users/Administrator/Desktop/submitted.csv";
	map<string, vector<double>> results = predPathTimes(predPath, busTimeUpStopCost, respath);

	//string finalpath = "C:/Users/Administrator/Desktop/submitted_revised.csv";
	//adjustPathTimes(basicpath, results, finalpath);

	system("pause");
	return 1;
}

set<string> loadTargetBusTimeUP(string datapath)
{
	set<string> res;
	ifstream fin(datapath.c_str());  //c_str()返回char型指针
	string str, substri;
	getline(fin, str);
	while (getline(fin, str))
	{
		vector<string> thisline = SplitLine(",", str);
		// 提取待预测的小时
		vector<string> hourMinSec = SplitLine(":", thisline[3]);
		string infokey = thisline[2] + "-" + hourMinSec[0] + "-" + thisline[6];
		res.insert(infokey);
	}
	fin.close();

	cout << "目标线路已读入完毕！" << endl;

	string respath = "C:/Users/Administrator/Desktop/targetPath.csv";
	ofstream fou(respath.c_str());
	for (set<string>::iterator it = res.begin(); it != res.end(); ++it)
		fou << *it << endl;
	fou.close();

	return res;
}

map<string, double> loadTrainBusTimeUPStop(string basicpath, set<string> targetBusTimeUp)
{

	map<string, vector<int>> results;

	cout << "开始处理训练集！" << endl;

	for (int i = 1008; i < 1025; i++)
	{
		// 存放这一天的时间、站点的信息
		map<string, map<int, int>> todayRecords;

		stringstream isis;
		isis << i;
		string stri;
		isis >> stri;
		string datapath = basicpath + stri + ".csv";

		cout << "	...读入数据 " << datapath << endl;

		ifstream fin(datapath.c_str());
		if (!fin)
		{
			cout << "Can not open file" << datapath << endl;
			system("pause");
		}
		string str, substri;
		// 跳过表头
		getline(fin, str);

		while (getline(fin, str))
		{
			vector<string> thisline = SplitLine(",", str);

			// 若时间段不对，直接跳过
			// 删除掉	晚上23点~早上6点以前的数据；
			vector<string> vecHourMinSec = SplitLine(":", thisline[2]);
			int thishour = atoi(vecHourMinSec[0].c_str());
			if (thishour >= 23)
				continue;
			if (thishour < 6)
				continue;

			int thismin = atoi(vecHourMinSec[1].c_str());
			int thissec = atoi(vecHourMinSec[2].c_str());

			// 生成当天的时间戳。
			int thisTime = thishour * 3600 + thismin * 60 + thissec;

			// 字段顺序
			// O_LINENO-0,O_TERMINALNO-1,O_Time-2,O_LONGITUDE-3,O_LATITUDE-4,O_SPEED-5,O_MIDDOOR-6,O_REARDOOR-7,O_FRONTDOOR-8,O_UP-9,O_RUN-10,O_NEXTSTATIONNO-11

			// 判断此记录，是否在“待预测线路”的附近时间之内
			{
				// 先放到本小时里面
				string strhour;
				stringstream isis;
				isis << thishour;
				isis >> strhour;
				string newkey = thisline[1] + "-" + strhour + "-" + thisline[9];

				if (targetBusTimeUp.count(newkey))
				{
					todayRecords[newkey].insert(make_pair(thisTime, atoi(thisline[11].c_str())));
				}
			}
			if (thismin < 20)
			{
				//可以算作是上一个小时的记录
				string strhour;
				stringstream isis;
				isis << thishour - 1;
				isis >> strhour;
				string newkey = thisline[1] + "-" + strhour + "-" + thisline[9];

				if (targetBusTimeUp.count(newkey))
				{
					todayRecords[newkey].insert(make_pair(thisTime, atoi(thisline[11].c_str())));
				}
			}
			if (thismin > 40)
			{
				//可以算作是下一个小时的记录
				string strhour;
				stringstream isis;
				isis << thishour + 1;
				isis >> strhour;
				string newkey = thisline[1] + "-" + strhour + "-" + thisline[9];

				if (targetBusTimeUp.count(newkey))
				{
					todayRecords[newkey].insert(make_pair(thisTime, atoi(thisline[11].c_str())));
				}
			}
		}
		fin.close();

		// 这一天的内容搞定了~~ 那么，接下来应该是根据这些信息，去判断到站时间

		cout << "	...估计到站时间 " << endl;
		// map<string, map<int, string>> todayRecords;
		for (map<string, map<int, int>>::iterator itbustime = todayRecords.begin(); itbustime != todayRecords.end(); ++itbustime)
		{

			// 处理这一bus-time-up的数据
			// 记录上一个站点
			int lastStop = itbustime->second.begin()->second;

			map<int, int> correctTimeStop; //用于存放“站点切换”的时刻

			for (map<int, int>::iterator ittime = itbustime->second.begin(); ittime != itbustime->second.end(); ++ittime)
			{
				// 仅考察“nextstop递增的情况”，且需要判断站点是否连续
				if (ittime->second > lastStop)
				{
					if (ittime->second = lastStop + 1)
					{
						// 表示stop是连续的，但还需要判断，时间间隔是否大于30秒；
						// 此处记录的时间是“结束lastStop时刻的时间”，切记，之后会用到
						if (correctTimeStop.empty())
						{
							correctTimeStop[ittime->first] = lastStop;
						}
						else
						{
							map<int, int>::iterator ittime2 = correctTimeStop.end();
							ittime2--;
							if (ittime->first - ittime2->first > 30)
								correctTimeStop[ittime->first] = lastStop;
						}
					}
					// 如果不连续，那么就粗暴地舍弃掉了！因为不知道是否是正确的！
				}
				lastStop = ittime->second;
			}

			//// 写一下这个correctTimeStop，用于观察
			//string path = basicpath + "tempCorrectTimePath.csv";
			//ofstream fou(path.c_str(), ios::app);
			//for (map<int, int>::iterator it = correctTimeStop.begin(); it != correctTimeStop.end(); ++it){
			//	fou << itbustime->first << "," << it->first << "," << it->second << endl;
			//}
			//fou.close();

			// 然后，需要计算每个站点的到站时间。在correctTimeStop里面，站点为x，表示从第x-1站到达第x站所需要的时间。
			// 在访问correctTimeStop的时候，需要注意，若遇到站点不连续的情况，比如 223,3;  434, 5;   556,6
			//      那么，无法计算从第2到第3站的时间消耗；也无法计算从第4站到第5站的时间消耗； 但是，可以计算从第5站到第6站的时间消耗
			//      据此规则，判断所有有效的“时间消耗”；然后，写入文件到results中
			map<int, int>::iterator ittime1 = correctTimeStop.begin();
			map<int, int>::iterator ittime2 = ittime1;
			ittime2++;

			// 如果第一个站是2，且是在整点时刻左右，就说明到达第二站的时间，应该算作是这个时刻减去整点
			if (ittime1->second == 2)
			{
				if (ittime1->first % 3600 <= 120)
				{
					//刚刚超过整点，那么就设置，站点2的到达时间为这个余数。
					string strstop;
					stringstream isis;
					isis << ittime1->second;
					isis >> strstop;
					string busTimeUpStop = itbustime->first + "-" + strstop;
					if (results.count(busTimeUpStop))
						results[busTimeUpStop].push_back(ittime1->first % 3600);
					else
					{
						vector<int> temp;
						temp.push_back(ittime1->first % 3600);
						results[busTimeUpStop] = temp;
					}
				}
			}

			// 根据上述连续站点的规则，判断有效的“时间消耗”
			while (ittime2 != correctTimeStop.end())
			{
				if (ittime2->second == ittime1->second + 1)
				{
					// 只有当站点连续的时候，才保留此结果
					string strstop;
					stringstream isis;
					isis << ittime2->second;
					isis >> strstop;
					string busTimeUpStop = itbustime->first + "-" + strstop;
					if (results.count(busTimeUpStop))
						results[busTimeUpStop].push_back(ittime2->first - ittime1->first);
					else
					{
						vector<int> temp;
						temp.push_back(ittime2->first - ittime1->first);
						results[busTimeUpStop] = temp;
					}
				}

				ittime1++;
				ittime2++;
			}

		} // 当天的记录处理完毕!

	} // 所有的日期都记录完毕！

	cout << "训练集处理完毕！--- " << endl;

	//// 最后，取中位数吧！
	//map<string, double> res;
	//for (map<string, vector<int>>::iterator itres = results.begin(); itres != results.end(); ++itres){
	//	multiset<int> temp;
	//	for (vector<int>::iterator ittime = itres->second.begin(); ittime != itres->second.end(); ++ittime){
	//		temp.insert(*ittime);
	//	}
	//	multiset<int>::iterator itit = temp.begin();
	//	for (size_t i = 0; i < temp.size() / 2; i++)
	//		itit++;
	//	res[itres->first] = *itit;
	//}

	// 最后，取平均数吧！
	map<string, double> res;
	for (map<string, vector<int>>::iterator itres = results.begin(); itres != results.end(); ++itres)
	{
		int tempsum = 0;
		for (vector<int>::iterator ittime = itres->second.begin(); ittime != itres->second.end(); ++ittime)
		{
			tempsum += *ittime;
		}

		res[itres->first] = double(tempsum) / double(itres->second.size());
	}

	// 最好把这个文件写出来！
	string respath = "C:/Users/Administrator/Desktop/busTimeUpStopCost.csv";
	ofstream fou(respath.c_str());
	for (map<string, double>::iterator it = res.begin(); it != res.end(); ++it)
		fou << it->first << "," << it->second << endl;
	fou.close();

	return res;
}

map<string, vector<double>> predPathTimes(string datapath, map<string, double> busTimeUpStopCost, string respath)
{
	cout << "开始预测最终结果 " << endl;

	map<string, vector<double>> results;

	ifstream fin(datapath.c_str());
	string str, substri;
	getline(fin, str);
	while (getline(fin, str))
	{
		vector<string> thisline = SplitLine(",", str);
		// 生成key
		vector<string> hourMinSec = SplitLine(":", thisline[3]);
		string infokey = thisline[2] + "-" + hourMinSec[0] + "-" + thisline[6];
		// 此时的infokey，是为了配合stop使用的
		int stStop = atoi(thisline[4].c_str()), enStop = atoi(thisline[5].c_str());

		vector<double> timeCosts;
		for (int stopi = stStop; stopi <= enStop; ++stopi)
		{
			string strStopi;
			stringstream isis;
			isis << stopi;
			isis >> strStopi;
			string busTimeUpStop = infokey + "-" + strStopi;
			if (busTimeUpStopCost.count(busTimeUpStop))
			{
				// 找到记录了，甚好！
				timeCosts.push_back(busTimeUpStopCost[busTimeUpStop]);
			}
			else
			{
				// 没找到，怎么办呢？直接填充一个数字吧~~ yin叔等选手讲，平均值大约在109或者128什么的，我就填110吧（本来也想填上下游时间的，可是懒得搞了）
				timeCosts.push_back(110);
			}
		}
		// 最后，再累加即可
		for (size_t i = 1; i < timeCosts.size(); i++)
		{
			timeCosts[i] += timeCosts[i - 1];
		}

		string thiskey;
		for (int i = 0; i < 6; i++)
			thiskey = thiskey + thisline[i] + ",";

		results[thiskey] = timeCosts;
	}
	fin.close();

	// 写出结果！
	ofstream fou(respath.c_str());
	fou << "O_DATA,O_LINENO,O_TERMINALNO,predHour,pred_start_stop_ID,pred_end_stop_ID,pred_timeStamps" << endl;

	for (map<string, vector<double>>::iterator itres = results.begin(); itres != results.end(); ++itres)
	{
		fou << itres->first;
		vector<double>::iterator itval = itres->second.begin();
		fou << *itval;
		++itval;
		while (itval != itres->second.end())
		{
			fou << ";" << *itval;
			++itval;
		}
		fou << endl;
	}
	fou.close();

	return results;
}

//void adjustPathTimes(string basicpath, map<string, vector<double>> results, string respath)
//{
//	cout << "根据当天的情况，纠正首次到站时间 " << endl;
//
//
//	for (int i = 1025; i < 1032; i++){
//		// 存放这一天的时间、站点的信息
//		map<string, map<int, int>> todayRecords;
//
//	}
//
//	return;
//}