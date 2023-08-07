# FeatCode
A take on LeetCode that brings a more realistic interview experience into the practice space for programmers looking to hone their code solving skills a little more.

## Web-Scraping LeetCode's top interview problems with JavaScript
This JS script was pasted into the console of chrome developer tools at https://leetcode.com/problemset/all/?listId=wpwgkgt&page=1 in order to scrape all of the top interview problem urls.  The urls are then printed to the console in csv format. From there, I manually copied the script output from the console and pasted it into a .txt file called 'data/leet_urls.txt'.

```
const results = [
    ['Problem_Name','Problem_URL']
];
var urls = document.getElementsByTagName('a');
for (urlIndex in urls) {
    const url = urls[urlIndex]
    if(url.href && url.href.indexOf('://')!==-1 && url.href.includes('/problems/') && !url.href.includes('/solution')) {
        let splits = url.href.split('/')
        let name = splits[splits.length - 2].replaceAll('-', ' ')
        results.push([name, url.href])
    }
}
const csvContent = results.map((line)=>{
    return line.map((cell)=>{
        let value = cell.replace(/[\f\n\v]*\n\s*/g, "\n").replace(/[\t\f ]+/g, ' ');
        value = value.replace(/\t/g, ' ').trim();
        return `${value}`
    }).join(',')
}).join("\n");
console.log(csvContent)
```
## Data cleaning with Python
Unfortunately, some repeat problems were copied into the file so I wrote preprocess/clean_data.py to get rid of the repeats and place the cleaned dataset into a new .txt file called "data/default_urls.txt".

## Creating the PROBLEMS database with SQLite and Python
At this point I could run fc_code/init_problems_db.py to initialize and populate the PROBLEMS table using the sqlite3 library and the "data/default_urls.txt" data file.
