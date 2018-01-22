var casper = require('casper').create({
    viewportSize : {width: 1920, height: 1080}
});
var fs = require('fs');

//var search = 'adidas Yeezy Boost 350 V2';
var counter = 1;
var numResults = 1;
var results = [];

casper.options.waitTimeout = 20000;
casper.start('https://www.stockx.com');

casper.then(function() {
    this.click('#header-nav-collapse > div > ul > li:nth-child(6) > a')
});

casper.then(function() {
    this.sendKeys('#login\\5b username\\5d', 'brian.zhang98@gmail.com', {keepFocus: true});
    this.sendKeys('#login\\5b password\\5d', 'BrianzhangsneakerX123_', {keepFocus: true});
    this.capture('login.jpg');
    this.sendKeys('#login\\5b password\\5d', casper.page.event.key.Enter , {keepFocus: true});
});

casper.waitForText("My Account", function() {
    this.capture('home.jpg');
    this.click('#home-search');
});

casper.then(function() {
    this.sendKeys('#home-search', this.cli.get("search"), {keepFocus: true});
    this.sendKeys('#home-search', casper.page.event.key.Enter , {keepFocus: true});
});

casper.waitForText("Sell", function() {
    // Code meant to scroll and automatically load any additional results
    //while(numResults != counter - 1) {
        //numResults = counter - 1;
        //this.scrollToBottom()
        //this.wait(500, function() {
    while(this.exists('#search-wrapper > div.search-results-grid > div:nth-child(' + counter + ')')){
        counter++
    }
    //}
    numResults = counter - 1;
    this.echo(numResults);

    if (numResults == 1) {
        this.click('#search-wrapper > div.search-results-grid > div > a')
        this.waitForText("Average Sale Price", function() {
            this.capture('tmp.jpg');
            fs.write('page.html', this.getHTML(), 'w');
        });
    }
    else {
        this.capture('search.jpg');
        fs.write('page.html', this.getHTML('#search-wrapper', true), 'w');
        this.capture('tmp.jpg');
    }
});

casper.run();