package cmd;
public class Option {

    public String optionTag;
    public String optionValue;

    public Option(String tag, String value)
    {
        this.optionTag = tag;
        this.optionValue = value;
    }

    public Option(String tag)
    {
        this.optionTag = tag;
        this.optionValue = "TRUE";
    }
}
