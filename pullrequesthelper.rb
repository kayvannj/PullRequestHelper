# Documentation: https://github.com/Homebrew/brew/blob/master/docs/Formula-Cookbook.md
#                http://www.rubydoc.info/github/Homebrew/brew/master/Formula

class Pullrequesthelper < Formula
  desc "A tool to help creating PullRequests on Github easier and automate some of the steps"
  homepage "https://github.com/kayvannj/PullRequestHelper"
  url "https://github.com/kayvannj/PullRequestHelper/archive/1.0.3.tar.gz"
  sha256 "e4b4020dec0c8a8ba2a6d4b38509a45df5416f1b1983ddd135d551cbada3be38"

  bottle do
    cellar :any_skip_relocation
    rebuild 2
    sha256 "c4b8a9bf7750571fd06084b6a2213c4c044467fa9a4b22a1338f9568114b9f3a" => :sierra
    sha256 "c7cbd9c2eeaa34510b936fa44e58da8239475e96582a4efdd2d5d57cd170432a" => :el_capitan
    sha256 "157caf5eecbc9feaead712675e575c8c2414ee2fdc54fe062cd849cc83033aeb" => :yosemite
    sha256 "2d7764d897c93c87ad3bc36595118e0adef3e275912c5126b5c63574c689a624" => :mavericks
  end

  resource "requests" do
    url "https://pypi.python.org/packages/5b/0b/34be574b1ec997247796e5d516f3a6b6509c4e064f2885a96ed885ce7579/requests-2.12.4.tar.gz#md5=acdb48888a9d3c7309da12fc7f83fedb"
    sha256 "ed98431a0631e309bb4b63c81d561c1654822cb103de1ac7b47e45c26be7ae34"
  end

  def install
    
    resource("requests").stage { system "python", *Language::Python.setup_install_args(libexec/"vendor") }
    
    etc.install "prh_config.py"
    inreplace "prh", "config_file_path", "#{etc}"
    bin.install "prh"

  end

  
end
