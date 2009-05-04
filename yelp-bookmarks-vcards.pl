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

    open my $out, ">:utf8", $self->output;
    print $out $addr->export;

    printf "%d contacts exported to %s\n", scalar @{$self->contacts}, $self->output;
}

package main;
Yelp::Exporter->new(yelp_userid => $ARGV[0])->run;

