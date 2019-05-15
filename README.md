# ZhiDuoShaoApi

用户表：
该表存储用户的收藏、设置等信息
bitmap组织方式："23100...0"，下标为i的数字表示第i个词背了多少遍，只能是1位数
word_collected组织方式："1,23,452,1,0..."，第i个数字表示收藏了词典中的哪个词
yiju_collect存储的是每日一句的id
word_collect表示的是收藏的背词中的词
dictionary_collect
study_history组织方式："2018-1-1:2,2014-2-5:4,..."，逗号分隔每天的信息，冒号分隔日期与背词数

word表：
150词（数量可能不是150）
一词多义被存储为不同的词
sentence：该词来自哪一句
article：该词的文章的标题
book_id：该词来自哪本书，书的id

词典表：
sentence：该词来自哪一句
source：该词来自于哪篇文章

yiju表：
以日期为主键，存储了每个日期对应的yiju，即使某个日期没有到，也已提前存储了该日对应的yiju