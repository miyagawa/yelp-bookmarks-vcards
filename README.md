yelp-bookmarks-vcards.pl - Export your Yelp bookmarks to vCards (.vcs) file

## What is this

Grabs your favorite businesses from Yelp bookmarks and export them as vCard contacts. Then you can import the vCard to your Mac OS X Address Book or Google Contacts.

## Requirements

Perl (5.8.1 or over recommended) and required CPAN modules: Any::Moose, Mouse (or Moose), JSON, LWP, URI and Text::vCard. Don't want to install all of these? Try [the web version](http://blog.bulknews.net/yelp-bookmarks-vcards.cgi).

## How to run it

`./yelp-bookmarks-vcards.pl YOUR-YELP-USERID`

You can find your Yelp user id by going to your Yelp bookmarks and see it in the URL `/user_details_bookmarks?userid=XXXXX`. For example my userid is `FikttuWnTGR1l09gokcwtw`.

By default the script writes vCard file as `yelp.vcf` under your home directory. You can change the path with `--ouput` command line switch.

## AUTHOR

Tatsuhiko Miyagawa

## LICENSE

Same as Perl (Artistic and GPL)

