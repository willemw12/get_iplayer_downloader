# Maintainer: Mark Foxwell <fastfret79@archlinux.org.uk>
# Contributor: AshtonBRSC <michael@ashtonbrsc.co.uk>
# Contributor: pluckypigeon <pluckypigeon@ArchForums.com>
# Contributor: canton7
#PATCH
# Contributor: willemw <willemw12@gmail.com>

#PATCH
#pkgname=get_iplayer-git
pkgname=get_iplayer-patched-git

pkgver=598.f7fae0f
pkgrel=1
pkgdesc="Allows you to download or stream any iPlayer programme from the BBC in H.264 (Quicktime/mp4) format, any radio programmes in MP3 or RealAudio format"
arch=('any')
url="http://www.infradead.org/get_iplayer/html/get_iplayer.html"
license=('GPL3')
depends=('perl-libwww' 'perl-html-parser' 'perl-www-mechanize' 'perl-http-cookies' 'perl-net-http')
optdepends=(
  'rtmpdump: record high-quality flash-based content'
  'flvstreamer: download files that are in flash (flv) format'
  'ffmpeg: convert flash (flv) files'
  'atomicparsley: add tags to MP4 files'
  'id3v2: add basic tags to MP3 files (if perl-mp3-tag not installed)'
  'lame: re-encode Real files into MP3'
  'mplayer: download files that are in Real or WMA format'
  'perl-mp3-tag: add tags to MP3 files'
  'perl-xml-simple: Series and Brand pid parsing'
  'vlc: download files in that are n95 format')
makedepends=('git')
conflicts=('get_iplayer')
provides=('get_iplayer')
source=($pkgname::git://git.infradead.org/get_iplayer.git)
md5sums=(SKIP)

pkgver() {
  cd "$srcdir/$pkgname"
  echo $(git rev-list --count HEAD).$(git rev-parse --short HEAD)
}

build() {
  cd "$srcdir/$pkgname"

  # Apply the following patches
  #
  ##my $info_limit      = 40;
  #my $info_limit      = 200;
  #
  ##$mp3->select_id3v2_frame_by_descr('COMM(eng,#0)[]', $tags->{comment});
  #$mp3->select_id3v2_frame_by_descr('COMM(eng,#0)[]', $tags->{longDescription});
  #
  ##'--COMM', $tags->{comment},
  #'--COMM', $tags->{longDescription},

  #PATCH increase download list size
  sed -i "s|^my \$info_limit.*|\n#PATCH\n#&\nmy \$info_limit      = 200;\n|" get_iplayer

  #PATCH store full description in id3v2 comment tag. Preserve indentation in the patch
  sed -i "s|\(^[ \t]*\)\(\$mp3->select_id3v2_frame_by_descr('COMM(eng,#0)\[\]', \$tags->{comment});.*\)|\n\1#PATCH\n\1#\2\n\1\$mp3->select_id3v2_frame_by_descr('COMM(eng,#0)\[\]', \$tags->{longDescription});\n|" get_iplayer
  sed -i "s|\(^[ \t]*\)\('--COMM', \$tags->{comment},.*\)|\n\1#PATCH\n\1#\2\n\1'--COMM', \$tags->{longDescription},\n|" get_iplayer

  #PATCH disable Akamai
  sudo sed -i "s|\(^[ \t]*\)\(if ( \$cattribs->{kind} eq 'akamai' ) {.*\)|\n\1#PATCH\n\1#\2\n\1if ( \$cattribs->{kind} eq 'DISABLED_akamai' ) {\n|" get_iplayer

  # Check applied patches
  if [ $(grep "#PATCH" get_iplayer | wc -l) -ne 4 ]; then
    echo "ERROR: the number of lines patched in /usr/bin/get_iplayer is different than expected" >&2
  fi
}

package() {
  cd "$srcdir/$pkgname"
	install -m755 -D get_iplayer $pkgdir/usr/bin/get_iplayer
	install -m644 -D README.txt $pkgdir/usr/share/doc/get_iplayer/README.txt
	install -D -m644 get_iplayer.1 ${pkgdir}/usr/share/man/man1/get_iplayer.1
	install -m755 -d $pkgdir/usr/share/get_iplayer/plugins
	install -m644 plugins/*.plugin $pkgdir/usr/share/get_iplayer/plugins/
	install -m755 plugins/plugin.template $pkgdir/usr/share/get_iplayer/plugins/
}
