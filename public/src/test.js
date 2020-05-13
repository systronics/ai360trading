var savePageWE=require('./nodeSavePageWE');


savePageWE.scrape({ url: "https://github.com/systronics/googlepass/blob/master/Intraday.mht", path: "intraday.html" }).then(function ()
{
    console.log("ok");
});
