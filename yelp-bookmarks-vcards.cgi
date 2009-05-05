#!/usr/bin/perl
use strict;

package Yelp::Exporter;
use Any::Moose;
use JSON;
use LWP::UserAgent;
use URI;
use URI::QueryParam;
use Text::vCard;
use Text::vCard::Addressbook;

has cgi => (
    is => 'rw', isa => 'CGI',
);

has yelp_userid => (
    is => 'rw', isa => 'Str', required => 1,
);

has contacts => (
    is => 'rw', isa => 'ArrayRef',
);

has debug => (
    is => 'rw', isa => 'Bool', default => 0,
);

has agent => (
    is => 'rw', isa => 'LWP::UserAgent',
    default => sub { LWP::UserAgent->new },
    lazy => 1,
);

has output => (
    is => 'rw', isa => 'Str',
    default => sub { "$ENV{HOME}/yelp.vcf" },
);

sub run {
    my $self = shift;

    $self->scrape_yelp();
    $self->export_vcards();
}

sub scrape_yelp {
    my $self = shift;

    my $page = URI->new("http://www.yelp.com/user_details_bookmarks");
    $page->query_param(userid => $self->yelp_userid);

    my $resp = $self->agent->get($page);
    $resp->is_success or die "GET $page failed: " . $resp->status_line;

    my $content = $resp->content;
    $content =~ /Yelp\.biz_list = *(\[.*?\]);\s*$/ms;

    $self->contacts(JSON::from_json($1));
}

sub export_vcards {
    my $self = shift;

    my $addr = Text::vCard::Addressbook->new;
    for my $contact (@{$self->contacts}) {
        my $vcard = $addr->add_vcard();
        $vcard->fullname($contact->{name});
        $vcard->add_node({ node_type => 'ORG' })->name($contact->{name});
        my $addr = $vcard->add_node({ node_type => 'ADR' });
        $addr->country($contact->{country});
        $addr->post_code($contact->{zip});
        $addr->region($contact->{state});
        $addr->city($contact->{city});
        $addr->street($contact->{address1});
        my $phone = $vcard->add_node({ node_type => 'TEL' });
        $phone->add_types('work');
        $phone->value($contact->{phone});
        $vcard->add_node({ node_type => 'X-Yelp-ID' })->value($contact->{id});
        $vcard->add_node({ node_type => 'X-ABShowAs' })->value('COMPANY');
        $vcard->url("http://www.yelp.com/biz/" . $contact->{id});

        if ($contact->{latitude} && $contact->{longitude}) {
            my $geo = $vcard->add_node({ node_type => 'GEO' });
            $geo->lat($contact->{latitude});
            $geo->long($contact->{longitude});
        }
    }

    print $self->cgi->header(-type => 'text/x-vcard', -content_disposition => "attachment;filename=yelp-bookmarks.vcf");
    binmode STDOUT, ":utf8";
    print $addr->export;
}

package main;

use CGI;

my $q = CGI->new;

if (my $userid = $q->param('userid')) {
    $userid =~ s/.*userid=//;
    Yelp::Exporter->new(cgi => $q, yelp_userid => $userid)->run;
} else {
    print $q->header('text/html');
    print <<HTML;
<html>
<head>
 <title>Yelp Bookmarks to vCard</title>
 <link rel="stylesheet" href="http://miyagawa.github.com/screen.css" />
</head>
<body>
<div class="container">
 <h1>Yelp Bookmarks to vCard</h1>
 <p>Enter your Yelp! user ID (e.g. <a href="#" onclick="document.forms[0].userid.value='http://www.yelp.com/user_details_bookmarks?userid=FikttuWnTGR1l09gokcwtw';">FikttuWnTGR1l09gokcwtw</a>) or bookmarks URL and you'll get <a href="http://en.wikipedia.org/wiki/VCard">vCard</a> (.vcf) file exported, which you can import to Mac OS X Address Book or Google Contact.</p>
 <form action="./yelp-bookmarks-vcards.cgi">
  <input type="text" name="userid" value="http://www.yelp.com/user_details_bookmarks?userid=" size="64" />
  <input type="submit" value="OK" />
 </form>

 <div class="span-22" style="text-align:right;margin-top:5em">Developed by <a href="http://github.com/miyagawa">Tatsuhiko Miyagawa</a> with <a href="http://www.perl.org/">Perl</a>, <a href="http://search.cpan.org/dist/Moose">Moose</a>, <a href="http://search.cpan.org/dist/libwww-perl">LWP</a> and <a href="http://search.cpan.org/dist/Text-vCard">Text::vCard</a>.<br/>See the source code and the command line version at <a href="http://github.com/miyagawa/yelp-bookmarks-vcards">GitHub</a>.</div>
</div>
</body>
</html>
HTML
}


