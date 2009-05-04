yelp-bookmarks-vcards.pl - Export your Yelp bookmarks to vCards (.vcs) file

## Requirements

Perl (5.8.1 or over recommended) and required CPAN modules (Any::Moose, Mouse, JSON, LWP, URI and Text::vCard).

## How to run it

`./yelp-bookmarks-vcards.pl --yelp_userid=YOUR-YELP-USERID`

You can find your Yelp user id by going to your Yelp bookmarks and see it in the URL `/user_details_bookmarks?userid=XXXXX`. By default the script writes vCard file as `yelp.vcf` under your home directory. You can change the path with `--ouput` command line switch.

## AUTHOR

Tatsuhiko Miyagawa

## LICENSE

Same as Perl (Artistic and GPL)

