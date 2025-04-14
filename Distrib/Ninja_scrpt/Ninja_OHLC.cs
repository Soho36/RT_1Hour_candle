using System;
using System.IO;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;  // ← this is the key one
using NinjaTrader.NinjaScript;



// The namespace and class name must match NinjaTrader conventions
namespace NinjaTrader.NinjaScript.Strategies
{
    public class SaveOHLCVToFile : Strategy
    {
        [NinjaScriptProperty]
        [Display(Name = "File Path", Order = 1, GroupName = "Parameters")]
        public string FilePath { get; set; }
		
        private bool isLiveData = false;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Name = "SaveOHLCVToFile";
                Calculate = Calculate.OnBarClose;
                FilePath = @"C:\temp\OHLCVData.csv"; // default value shown in UI
            }
            else if (State == State.Realtime)
            {
                isLiveData = true;
            }
        }

        protected override void OnBarUpdate()
        {
            if (!isLiveData)
                return;

            double open = Open[0];
            double high = High[0];
            double low = Low[0];
            double close = Close[0];
            double volume = Volume[0];

            DateTime now = Time[0];
            string currentDate = now.ToString("yyyy.MM.dd");
            string currentTime = now.ToString("HH:mm");

            string dataLine = string.Join(";",
                Instrument.FullName,
                BarsPeriod.Value + BarsPeriod.BarsPeriodType.ToString(),
                currentDate,
                currentTime,
                open.ToString("F2"),
                high.ToString("F2"),
                low.ToString("F2"),
                close.ToString("F2"),
                volume.ToString("F2"));

            Print("New line saved to file: " + dataLine);
            File.AppendAllText(FilePath, dataLine + Environment.NewLine);
        }
    }
}